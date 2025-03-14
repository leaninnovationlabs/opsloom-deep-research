"""create aws cost table

Revision ID: 795abb481236
Revises: 007_combined_seed
Create Date: 2024-12-26 10:23:14.444432

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String, ForeignKey, Integer, Boolean
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '795abb481236'
down_revision: Union[str, None] = '007_combined_seed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    default_short_code='default'

    months = ['June', 'July', 'August', 'September']
    resources = ['EC2', 'Lambda', 'DynamoDB', 'S3']

    costs = [117, 219, 172, 33, 152, 271, 106, 56, 195, 344, 132, 48, 209, 294, 159, 73]
    over_budget_values = [False, False, True, False, False, True, False, True, False, True, False, False, True, True, False, True]

    if 'aws_cost' not in inspector.get_table_names():
        op.create_table(
            'aws_cost',
            Column('id', String(255), primary_key=True, nullable=False),
            Column('account_short_code', String(10), ForeignKey('account.short_code'), nullable=True),
            Column('resource_name', String(255), nullable=False),
            Column('month', String(255), nullable=False),
            Column('cost', Integer, nullable=False),
            Column('over_budget', Boolean, nullable=False)
        )

    for i in range(len(months)):
        for j in range(len(resources)):
            month = months[i]
            resource_name = resources[j]
            cost = costs[(i * 4) + j]
            over_budget = over_budget_values[(i * 4) + j]

            op.execute(
                sa.text("""
                    INSERT INTO aws_cost (
                        id, account_short_code, resource_name, month, cost, over_budget
                    ) VALUES (
                        :id, :account_short_code, :resource_name, :month, :cost, :over_budget
                    )
                """).bindparams(
                    id='11111111-1111-1111-1111-1111111111' + str(i) + str(j),
                    account_short_code=default_short_code,
                    resource_name=resource_name,
                    month=month,
                    cost=cost,
                    over_budget=over_budget
                )
            )


def downgrade() -> None:
    op.drop_table('aws_cost')
