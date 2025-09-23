# Azure provider for CloudViz platform

from cloudviz.providers.azure.extractor import AzureResourceExtractor
from cloudviz.providers.azure.factory import AzureProviderFactory
from cloudviz.providers.azure.models import AzureResource, AzureResourceType

__all__ = [
    "AzureResourceExtractor",
    "AzureProviderFactory",
    "AzureResource",
    "AzureResourceType",
]
