from typing import Optional
from pydantic import BaseModel
from psycopg2 import sql


class QueryParams(BaseModel):
    rate_number: Optional[str] = None
    legal_description: Optional[str] = None
    address: Optional[str] = None
    first_owner: Optional[str] = None
    use_code: Optional[str] = None
    rating_category: Optional[str] = None
    market_value: Optional[str] = None
    registered_extent: Optional[float] = None

    # Dependency function to create QueryParams
    def get_query_params(
        rate_number: Optional[str] = None,
        legal_description: Optional[str] = None,
        address: Optional[str] = None,
        first_owner: Optional[str] = None,
        use_code: Optional[str] = None,
        rating_category: Optional[str] = None,
        market_value: Optional[str] = None,
        registered_extent: Optional[float] = None
    ):
        return QueryParams(
            rate_number=rate_number,
            legal_description=legal_description,
            address=address,
            first_owner=first_owner,
            use_code=use_code,
            rating_category=rating_category,
            market_value=market_value,
            registered_extent=registered_extent
        )

    # Create a database query
    def create_query(self, table_name: str):
        # Define the base query
        base_query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))

        # List to hold conditions for SQL WHERE clause and their corresponding values
        conditions = []
        values = []

        # Check and append conditions based on which parameters are provided
        if self.rate_number:
            conditions.append(sql.SQL("rate_number = %s"))
            values.append(self.rate_number)
        if self.legal_description:
            conditions.append(sql.SQL("legal_description = %s"))
            values.append(self.legal_description)
        if self.address:
            conditions.append(sql.SQL("address = %s"))
            values.append(self.address)
        if self.first_owner:
            conditions.append(sql.SQL("first_owner = %s"))
            values.append(self.first_owner)
        if self.use_code:
            conditions.append(sql.SQL("use_code = %s"))
            values.append(self.use_code)
        if self.rating_category:
            conditions.append(sql.SQL("rating_category = %s"))
            values.append(self.rating_category)
        if self.market_value:
            conditions.append(sql.SQL("market_value = %s"))
            values.append(self.market_value)
        if self.registered_extent is not None:
            conditions.append(sql.SQL("registered_extent = %s"))
            values.append(self.registered_extent)

        # Combine the conditions into the WHERE clause if any exist
        if conditions:
            query = sql.SQL(" ").join(
                [base_query, sql.SQL("WHERE"), sql.SQL(" AND ").join(conditions)]
            )
        else:
            query = base_query

        return query, values
