"""
Data Pipeline Module

This module contains the master data orchestrator and related utilities
for coordinating data extraction, normalization, and integration across
multiple data sources for NFL player statistics.

Main Components:
- MasterDataOrchestrator: Central coordinator for all data operations
- Data normalization and validation utilities
- Progress tracking and error handling
"""

from .master_orchestrator import MasterDataOrchestrator, orchestrate_full_season_data

__all__ = ['MasterDataOrchestrator', 'orchestrate_full_season_data'] 