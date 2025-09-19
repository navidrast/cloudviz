# CloudViz Legacy PowerShell Module
# Modernized version of AzViz for backward compatibility
# Provides PowerShell-based Azure resource visualization

@{
    # Module manifest for CloudVizLegacy
    ModuleVersion = '1.0.0'
    GUID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    Author = 'CloudViz Team'
    CompanyName = 'CloudViz'
    Copyright = '(c) 2025 CloudViz. All rights reserved.'
    Description = 'CloudViz Legacy PowerShell module for Azure resource visualization and extraction. Modernized from AzViz.'
    
    # Minimum PowerShell version
    PowerShellVersion = '5.1'
    
    # Required modules
    RequiredModules = @('Az.Resources', 'Az.Profile', 'Az.Storage')
    
    # Functions to export
    FunctionsToExport = @(
        'Get-CloudVizResourceInventory',
        'Export-CloudVizDiagram', 
        'Get-CloudVizResourceRelationships',
        'Set-CloudVizConfiguration',
        'Get-CloudVizConfiguration',
        'Test-CloudVizConnection',
        'Get-CloudVizSupportedResourceTypes',
        'Export-CloudVizResourceData',
        'Import-CloudVizResourceData',
        'New-CloudVizResourceMap'
    )
    
    # Cmdlets to export
    CmdletsToExport = @()
    
    # Variables to export
    VariablesToExport = @()
    
    # Aliases to export
    AliasesToExport = @(
        'Get-AzVizResourceInventory',  # Legacy alias
        'Export-AzVizDiagram',         # Legacy alias
        'cloudviz'                     # Short alias
    )
    
    # Private data
    PrivateData = @{
        PSData = @{
            Tags = @('Azure', 'Visualization', 'Infrastructure', 'CloudViz', 'Diagram', 'Resources')
            LicenseUri = 'https://github.com/navidrast/cloudviz/blob/main/LICENSE'
            ProjectUri = 'https://github.com/navidrast/cloudviz'
            ReleaseNotes = 'CloudViz Legacy v1.0.0 - Modernized Azure resource visualization'
        }
    }
}
