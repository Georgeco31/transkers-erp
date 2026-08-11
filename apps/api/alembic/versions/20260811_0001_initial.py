"""Initial Transker ERP schema."""
from alembic import op
import sqlalchemy as sa

revision = "20260811_0001"
down_revision = None
branch_labels = None
depends_on = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("username", sa.String(80), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False), *timestamps(),
        sa.CheckConstraint("role IN ('admin', 'operator')", name="ck_users_role"), sa.UniqueConstraint("username"))
    op.create_index("ix_users_username", "users", ["username"]); op.create_index("ix_users_role", "users", ["role"]); op.create_index("ix_users_is_active", "users", ["is_active"])

    op.create_table("clients",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(180), nullable=False),
        sa.Column("tax_id", sa.String(50)), sa.Column("phone", sa.String(50)), sa.Column("notes", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=False), *timestamps())
    op.create_index("ix_clients_name", "clients", ["name"]); op.create_index("ix_clients_is_active", "clients", ["is_active"])

    op.create_table("drivers",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(180), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False), *timestamps())
    op.create_index("ix_drivers_name", "drivers", ["name"]); op.create_index("ix_drivers_is_active", "drivers", ["is_active"])

    op.create_table("vehicles",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("plate", sa.String(30), nullable=False),
        sa.Column("brand", sa.String(80)), sa.Column("model", sa.String(80)), sa.Column("year", sa.Integer()),
        sa.Column("notes", sa.Text()), sa.Column("is_active", sa.Boolean(), nullable=False), *timestamps(),
        sa.UniqueConstraint("plate"))
    op.create_index("ix_vehicles_plate", "vehicles", ["plate"]); op.create_index("ix_vehicles_is_active", "vehicles", ["is_active"])

    op.create_table("trip_expense_categories",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name"))
    op.create_index("ix_trip_expense_categories_is_active", "trip_expense_categories", ["is_active"])

    op.create_table("trips",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("code", sa.String(30), nullable=False),
        sa.Column("trip_date", sa.Date(), nullable=False),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), sa.ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("driver_id", sa.Integer(), sa.ForeignKey("drivers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("origin", sa.String(180)), sa.Column("destination", sa.String(180)), sa.Column("description", sa.Text()),
        sa.Column("agreed_price", sa.Numeric(14, 2), nullable=False), sa.Column("status", sa.String(20), nullable=False),
        sa.Column("notes", sa.Text()), sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        *timestamps(), sa.CheckConstraint("agreed_price >= 0", name="ck_trips_price_nonnegative"),
        sa.CheckConstraint("status IN ('draft', 'completed', 'cancelled')", name="ck_trips_status"), sa.UniqueConstraint("code"))
    for name, cols in [("ix_trips_code", ["code"]), ("ix_trips_trip_date", ["trip_date"]), ("ix_trips_client_id", ["client_id"]),
                       ("ix_trips_vehicle_id", ["vehicle_id"]), ("ix_trips_driver_id", ["driver_id"]), ("ix_trips_status", ["status"]),
                       ("ix_trips_client_date", ["client_id", "trip_date"]), ("ix_trips_vehicle_date", ["vehicle_id", "trip_date"]),
                       ("ix_trips_driver_date", ["driver_id", "trip_date"])]: op.create_index(name, "trips", cols)

    op.create_table("trip_expenses",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("trip_id", sa.Integer(), sa.ForeignKey("trips.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("trip_expense_categories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False), sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("description", sa.Text()), sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        *timestamps(), sa.CheckConstraint("amount > 0", name="ck_trip_expenses_amount_positive"))
    for name, cols in [("ix_trip_expenses_trip_id", ["trip_id"]), ("ix_trip_expenses_category_id", ["category_id"]), ("ix_trip_expenses_expense_date", ["expense_date"])]: op.create_index(name, "trip_expenses", cols)

    op.create_table("vehicle_expenses",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("vehicle_id", sa.Integer(), sa.ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("expense_type", sa.String(20), nullable=False), sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False), sa.Column("description", sa.Text(), nullable=False),
        sa.Column("odometer", sa.Integer()), sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        *timestamps(), sa.CheckConstraint("amount > 0", name="ck_vehicle_expenses_amount_positive"),
        sa.CheckConstraint("expense_type IN ('maintenance', 'repair')", name="ck_vehicle_expenses_type"))
    for name, cols in [("ix_vehicle_expenses_vehicle_id", ["vehicle_id"]), ("ix_vehicle_expenses_expense_type", ["expense_type"]), ("ix_vehicle_expenses_expense_date", ["expense_date"])]: op.create_index(name, "vehicle_expenses", cols)

    op.create_table("client_payments",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False), sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("payment_method", sa.String(80)), sa.Column("reference", sa.String(120)), sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_client_payments_amount_positive"))
    op.create_index("ix_client_payments_client_id", "client_payments", ["client_id"]); op.create_index("ix_client_payments_payment_date", "client_payments", ["payment_date"])

    op.create_table("payment_allocations",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("payment_id", sa.Integer(), sa.ForeignKey("client_payments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("trip_id", sa.Integer(), sa.ForeignKey("trips.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_payment_allocations_amount_positive"),
        sa.UniqueConstraint("payment_id", "trip_id", name="uq_payment_allocation_payment_trip"))
    op.create_index("ix_payment_allocations_payment_id", "payment_allocations", ["payment_id"]); op.create_index("ix_payment_allocations_trip_id", "payment_allocations", ["trip_id"])


def downgrade() -> None:
    for table in ["payment_allocations", "client_payments", "vehicle_expenses", "trip_expenses", "trips", "trip_expense_categories", "vehicles", "drivers", "clients", "users"]:
        op.drop_table(table)

