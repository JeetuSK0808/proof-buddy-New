# Generated manually on 2025-12-29
# 2026-06: dedup rewritten from MySQL-only multi-table DELETE (which breaks
# SQLite/Postgres local dev) to a backend-agnostic RunPython. Databases that
# already applied the original version are unaffected (same app/number).
from django.db import migrations, models


def remove_duplicate_proof_lines(apps, schema_editor):
    """Keep only the most recent row (highest id) for each
    (proof, case, side, line_number) combination."""
    InductionProofLine = apps.get_model('induction_api', 'InductionProofLine')
    seen = {}
    duplicate_ids = []
    for row_id, proof_id, case, side, line_number in (
        InductionProofLine.objects.order_by('-id')
        .values_list('id', 'proof_id', 'case', 'side', 'line_number')
    ):
        key = (proof_id, case, side, line_number)
        if key in seen:
            duplicate_ids.append(row_id)
        else:
            seen[key] = row_id
    if duplicate_ids:
        InductionProofLine.objects.filter(id__in=duplicate_ids).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('induction_api', '0004_inductionproofline_selected_node'),
    ]

    operations = [
        # First, remove duplicate proof lines (keep the most recent one for
        # each unique combination), so the constraint below can be added.
        migrations.RunPython(
            remove_duplicate_proof_lines,
            reverse_code=migrations.RunPython.noop,
        ),

        # Then add the unique constraint
        migrations.AddConstraint(
            model_name='inductionproofline',
            constraint=models.UniqueConstraint(
                fields=['proof', 'case', 'side', 'line_number'],
                name='unique_proof_line'
            ),
        ),
    ]
