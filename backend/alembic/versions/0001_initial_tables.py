"""initial tables

Revision ID: 0001
Revises:
Create Date: 2026-05-17

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # plans
    op.create_table('plans',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('price_monthly', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('max_products', sa.Integer(), nullable=False),
        sa.Column('leads_per_month', sa.Integer(), nullable=False),
        sa.Column('featured_listings', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('has_analytics', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('has_whatsapp', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('support_level', sa.String(50), nullable=False, server_default='none'),
        sa.Column('razorpay_plan_id', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )

    # users
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(15), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, server_default='buyer'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('google_id', sa.String(100), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('phone')
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_phone', 'users', ['phone'])

    # companies
    op.create_table('companies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(200), nullable=False),
        sa.Column('gst_number', sa.String(20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('state', sa.String(100), nullable=False),
        sa.Column('pincode', sa.String(10), nullable=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('phone', sa.String(15), nullable=False),
        sa.Column('website', sa.String(300), nullable=True),
        sa.Column('year_established', sa.Integer(), nullable=True),
        sa.Column('employee_count', sa.String(50), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('total_leads', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('idx_companies_slug', 'companies', ['slug'])
    op.create_index('idx_companies_city', 'companies', ['city'])
    op.create_index('idx_companies_category', 'companies', ['category'])
    op.create_index('idx_companies_verified', 'companies', ['is_verified'])

    # categories
    op.create_table('categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('product_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('idx_categories_slug', 'categories', ['slug'])

    # products
    op.create_table('products',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('slug', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('price_min', sa.DECIMAL(12, 2), nullable=True),
        sa.Column('price_max', sa.DECIMAL(12, 2), nullable=True),
        sa.Column('unit', sa.String(50), nullable=False, server_default='piece'),
        sa.Column('moq', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('images', postgresql.ARRAY(sa.Text()), nullable=False, server_default='{}'),
        sa.Column('tags', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('specifications', postgresql.JSONB(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('inquiry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('idx_products_company', 'products', ['company_id'])
    op.create_index('idx_products_category', 'products', ['category_id'])
    op.create_index('idx_products_status', 'products', ['status'])
    op.create_index('idx_products_featured', 'products', ['is_featured'])
    op.create_index('idx_products_created', 'products', ['created_at'])

    # subscriptions
    op.create_table('subscriptions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('razorpay_sub_id', sa.String(100), nullable=True),
        sa.Column('razorpay_customer_id', sa.String(100), nullable=True),
        sa.Column('status', sa.String(30), nullable=False, server_default='trial'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('trial_end', sa.Date(), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_payment_at', sa.DateTime(), nullable=True),
        sa.Column('next_billing_at', sa.DateTime(), nullable=True),
        sa.Column('amount_paid', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id')
    )

    # inquiries
    op.create_table('inquiries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('buyer_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(30), nullable=False, server_default='new'),
        sa.Column('seller_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_inquiries_buyer', 'inquiries', ['buyer_id'])
    op.create_index('idx_inquiries_company', 'inquiries', ['company_id'])
    op.create_index('idx_inquiries_status', 'inquiries', ['status'])

    # leads
    op.create_table('leads',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('inquiry_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('buyer_name', sa.String(100), nullable=False),
        sa.Column('buyer_phone', sa.String(15), nullable=False),
        sa.Column('buyer_email', sa.String(255), nullable=False),
        sa.Column('buyer_city', sa.String(100), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(50), nullable=False, server_default='inquiry'),
        sa.Column('is_viewed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['inquiry_id'], ['inquiries.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # seed plans
    op.execute("""
        INSERT INTO plans (name, price_monthly, max_products, leads_per_month, featured_listings, has_analytics, has_whatsapp, support_level)
        VALUES
            ('Free',       0,    5,   3,  0, false, false, 'none'),
            ('Basic',      999,  50,  20, 0, true,  true,  'email'),
            ('Pro',        2499, 200, -1, 2, true,  true,  'priority'),
            ('Enterprise', 5999, -1,  -1, 5, true,  true,  'dedicated')
    """)


def downgrade() -> None:
    op.drop_table('leads')
    op.drop_table('inquiries')
    op.drop_table('subscriptions')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_table('companies')
    op.drop_table('users')
    op.drop_table('plans')
