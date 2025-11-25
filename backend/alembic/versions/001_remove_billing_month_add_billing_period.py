"""remove_billing_month_add_billing_period

Revision ID: 001
Revises: 
Create Date: 2025-11-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the constraint trigger first
    op.execute("DROP TRIGGER IF EXISTS chk_billing_month_firstday ON billing_runs;")
    
    # Drop the function
    op.execute("DROP FUNCTION IF EXISTS enforce_first_day_month();")
    
    # Drop the old UNIQUE constraint
    op.drop_constraint('uniq_billing_run', 'billing_runs', type_='unique')
    
    # Add new columns
    op.add_column('billing_runs', sa.Column('billing_start', sa.Date(), nullable=False, server_default='2025-01-01'))
    op.add_column('billing_runs', sa.Column('billing_end', sa.Date(), nullable=False, server_default='2025-02-01'))
    
    # Drop the old billing_month column
    op.drop_column('billing_runs', 'billing_month')
    
    # Add new UNIQUE constraint
    op.create_unique_constraint('uniq_billing_run', 'billing_runs', ['client_id', 'vendor_id', 'billing_start'])
    
    # Add check constraint for billing_end > billing_start
    op.create_check_constraint(
        'chk_billing_period',
        'billing_runs',
        'billing_end > billing_start'
    )


def downgrade() -> None:
    # Remove check constraint
    op.drop_constraint('chk_billing_period', 'billing_runs', type_='check')
    
    # Drop new UNIQUE constraint
    op.drop_constraint('uniq_billing_run', 'billing_runs', type_='unique')
    
    # Add back billing_month column
    op.add_column('billing_runs', sa.Column('billing_month', sa.Date(), nullable=False, server_default='2025-01-01'))
    
    # Drop new columns
    op.drop_column('billing_runs', 'billing_end')
    op.drop_column('billing_runs', 'billing_start')
    
    # Recreate old UNIQUE constraint
    op.create_unique_constraint('uniq_billing_run', 'billing_runs', ['client_id', 'vendor_id', 'billing_month'])
    
    # Recreate function and trigger
    op.execute("""
        CREATE FUNCTION enforce_first_day_month()
        RETURNS TRIGGER LANGUAGE plpgsql AS $$
        BEGIN
          IF date_trunc('month', NEW.billing_month) <> NEW.billing_month THEN
            RAISE EXCEPTION 'billing_month must be the first day of the month';
          END IF;
          RETURN NEW;
        END;
        $$;
    """)
    
    op.execute("""
        CREATE CONSTRAINT TRIGGER chk_billing_month_firstday
        AFTER INSERT OR UPDATE ON billing_runs
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION enforce_first_day_month();
    """)

