"""
Database migrations for SafeLane.

Handles schema evolution without requiring external migration tools.
"""
import logging
from sqlalchemy import text
from platform_app.server.services.db import engine

logger = logging.getLogger('safelane.platform')


async def add_missing_columns():
    """
    Add any missing columns to existing tables.
    This is called during app startup to handle schema evolution.
    """
    async with engine.begin() as conn:
        # Add rollback_strategy column if it doesn't exist
        result = await conn.execute(
            text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name='registrations' AND column_name='rollback_strategy'
            )
            """)
        )
        if not (await result.scalar()):
            logger.info("Adding rollback_strategy column to registrations table...")
            await conn.execute(
                text("""
                ALTER TABLE registrations 
                ADD COLUMN rollback_strategy VARCHAR DEFAULT 'branch' NOT NULL
                """)
            )
            logger.info("✓ rollback_strategy column added")

        # Add custom_holiday_dates column if it doesn't exist
        result = await conn.execute(
            text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name='registrations' AND column_name='custom_holiday_dates'
            )
            """)
        )
        if not (await result.scalar()):
            logger.info("Adding custom_holiday_dates column to registrations table...")
            await conn.execute(
                text("""
                ALTER TABLE registrations 
                ADD COLUMN custom_holiday_dates TEXT
                """)
            )
            logger.info("✓ custom_holiday_dates column added")

        # Add deploy_window_start_utc column if it doesn't exist
        result = await conn.execute(
            text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name='registrations' AND column_name='deploy_window_start_utc'
            )
            """)
        )
        if not (await result.scalar()):
            logger.info("Adding deploy_window_start_utc column to registrations table...")
            await conn.execute(
                text("""
                ALTER TABLE registrations 
                ADD COLUMN deploy_window_start_utc INTEGER
                """)
            )
            logger.info("✓ deploy_window_start_utc column added")

        # Add deploy_window_end_utc column if it doesn't exist
        result = await conn.execute(
            text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name='registrations' AND column_name='deploy_window_end_utc'
            )
            """)
        )
        if not (await result.scalar()):
            logger.info("Adding deploy_window_end_utc column to registrations table...")
            await conn.execute(
                text("""
                ALTER TABLE registrations 
                ADD COLUMN deploy_window_end_utc INTEGER
                """)
            )
            logger.info("✓ deploy_window_end_utc column added")

