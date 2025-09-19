# CloudViz Legacy PowerShell Module
# Modernized from AzViz - Azure Resource Visualization
# Author: CloudViz Team
# Version: 1.0.0

#Requires -Modules Az.Resources, Az.Profile

# Global configuration
$Script:CloudVizConfig = @{
    OutputPath = "$env:TEMP\CloudViz"
    LogLevel = 'Info'
    MaxConcurrentJobs = 5
    TimeoutMinutes = 30
    IncludePreview = $false
    DiagramFormats = @('mermaid', 'dot', 'png', 'svg')
    DefaultFormat = 'mermaid'
    Theme = 'professional'
}

# Resource type mappings for visualization
$Script:ResourceTypeMap = @{
    'Microsoft.Compute/virtualMachines' = @{ Icon = '🖥️'; Category = 'Compute'; Color = '#0078D4' }
    'Microsoft.Storage/storageAccounts' = @{ Icon = '💾'; Category = 'Storage'; Color = '#00BCF2' }
    'Microsoft.Network/virtualNetworks' = @{ Icon = '🌐'; Category = 'Network'; Color = '#7FBA00' }
    'Microsoft.Web/sites' = @{ Icon = '🌍'; Category = 'Web'; Color = '#FE8C00' }
    'Microsoft.Sql/servers' = @{ Icon = '🗄️'; Category = 'Database'; Color = '#FF6C00' }
    'Microsoft.KeyVault/vaults' = @{ Icon = '🔐'; Category = 'Security'; Color = '#5C2D91' }
    'Microsoft.ContainerService/managedClusters' = @{ Icon = '📦'; Category = 'Container'; Color = '#0078D4' }
    'Microsoft.Resources/resourceGroups' = @{ Icon = '📁'; Category = 'Management'; Color = '#68217A' }
}

#region Configuration Functions

function Set-CloudVizConfiguration {
    <#
    .SYNOPSIS
    Configure CloudViz settings
    
    .DESCRIPTION
    Set global configuration options for CloudViz operations
    
    .PARAMETER OutputPath
    Directory for output files
    
    .PARAMETER LogLevel
    Logging level (Debug, Info, Warning, Error)
    
    .PARAMETER MaxConcurrentJobs
    Maximum number of concurrent PowerShell jobs
    
    .PARAMETER TimeoutMinutes
    Timeout for operations in minutes
    
    .PARAMETER DefaultFormat
    Default output format for diagrams
    
    .PARAMETER Theme
    Visual theme for diagrams
    
    .EXAMPLE
    Set-CloudVizConfiguration -OutputPath "C:\CloudViz" -LogLevel Info
    #>
    [CmdletBinding()]
    param(
        [string]$OutputPath,
        [ValidateSet('Debug', 'Info', 'Warning', 'Error')]
        [string]$LogLevel,
        [int]$MaxConcurrentJobs,
        [int]$TimeoutMinutes,
        [ValidateSet('mermaid', 'dot', 'png', 'svg')]
        [string]$DefaultFormat,
        [ValidateSet('professional', 'dark', 'light', 'minimal')]
        [string]$Theme
    )
    
    if ($OutputPath) { $Script:CloudVizConfig.OutputPath = $OutputPath }
    if ($LogLevel) { $Script:CloudVizConfig.LogLevel = $LogLevel }
    if ($MaxConcurrentJobs) { $Script:CloudVizConfig.MaxConcurrentJobs = $MaxConcurrentJobs }
    if ($TimeoutMinutes) { $Script:CloudVizConfig.TimeoutMinutes = $TimeoutMinutes }
    if ($DefaultFormat) { $Script:CloudVizConfig.DefaultFormat = $DefaultFormat }
    if ($Theme) { $Script:CloudVizConfig.Theme = $Theme }
    
    Write-CloudVizLog "Configuration updated" -Level Info
}

function Get-CloudVizConfiguration {
    <#
    .SYNOPSIS
    Get current CloudViz configuration
    
    .DESCRIPTION
    Returns the current CloudViz configuration settings
    
    .EXAMPLE
    Get-CloudVizConfiguration
    #>
    [CmdletBinding()]
    param()
    
    return $Script:CloudVizConfig
}

#endregion

#region Utility Functions

function Write-CloudVizLog {
    <#
    .SYNOPSIS
    Write log message with timestamp
    
    .PARAMETER Message
    Log message
    
    .PARAMETER Level
    Log level
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Message,
        
        [ValidateSet('Debug', 'Info', 'Warning', 'Error')]
        [string]$Level = 'Info'
    )
    
    $levels = @{ Debug = 0; Info = 1; Warning = 2; Error = 3 }
    $configLevel = $levels[$Script:CloudVizConfig.LogLevel]
    $messageLevel = $levels[$Level]
    
    if ($messageLevel -ge $configLevel) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $logMessage = "[$timestamp] [$Level] $Message"
        
        switch ($Level) {
            'Error' { Write-Error $logMessage }
            'Warning' { Write-Warning $logMessage }
            'Debug' { Write-Debug $logMessage }
            default { Write-Host $logMessage }
        }
    }
}

function Test-CloudVizConnection {
    <#
    .SYNOPSIS
    Test Azure connection and permissions
    
    .DESCRIPTION
    Verify that the current session has proper Azure authentication and permissions
    
    .EXAMPLE
    Test-CloudVizConnection
    #>
    [CmdletBinding()]
    param()
    
    try {
        Write-CloudVizLog "Testing Azure connection..." -Level Info
        
        # Test basic connection
        $context = Get-AzContext
        if (-not $context) {
            throw "No Azure context found. Please run Connect-AzAccount first."
        }
        
        Write-CloudVizLog "Connected to Azure as: $($context.Account.Id)" -Level Info
        Write-CloudVizLog "Subscription: $($context.Subscription.Name) ($($context.Subscription.Id))" -Level Info
        
        # Test permissions by listing resource groups
        $resourceGroups = Get-AzResourceGroup -ErrorAction Stop | Select-Object -First 1
        Write-CloudVizLog "Permissions verified - can access resource groups" -Level Info
        
        return $true
    }
    catch {
        Write-CloudVizLog "Connection test failed: $($_.Exception.Message)" -Level Error
        return $false
    }
}

function Get-CloudVizSupportedResourceTypes {
    <#
    .SYNOPSIS
    Get list of supported Azure resource types
    
    .DESCRIPTION
    Returns a list of Azure resource types that CloudViz can visualize
    
    .EXAMPLE
    Get-CloudVizSupportedResourceTypes
    #>
    [CmdletBinding()]
    param()
    
    return $Script:ResourceTypeMap.Keys | Sort-Object
}

#endregion

#region Resource Discovery Functions

function Get-CloudVizResourceInventory {
    <#
    .SYNOPSIS
    Get comprehensive Azure resource inventory
    
    .DESCRIPTION
    Extracts detailed information about Azure resources from specified scope
    
    .PARAMETER SubscriptionId
    Azure subscription ID to scan
    
    .PARAMETER ResourceGroupName
    Resource group name to scan (optional)
    
    .PARAMETER ResourceType
    Filter by specific resource types
    
    .PARAMETER Tag
    Filter by resource tags (hashtable)
    
    .PARAMETER IncludePreview
    Include preview/beta resources
    
    .PARAMETER Parallel
    Use parallel processing for faster extraction
    
    .EXAMPLE
    Get-CloudVizResourceInventory -SubscriptionId "12345678-1234-1234-1234-123456789012"
    
    .EXAMPLE
    Get-CloudVizResourceInventory -ResourceGroupName "MyResourceGroup" -ResourceType "Microsoft.Compute/virtualMachines"
    
    .EXAMPLE
    Get-CloudVizResourceInventory -Tag @{Environment="Production"; Owner="TeamA"}
    #>
    [CmdletBinding()]
    param(
        [string]$SubscriptionId,
        [string]$ResourceGroupName,
        [string[]]$ResourceType,
        [hashtable]$Tag,
        [switch]$IncludePreview,
        [switch]$Parallel
    )
    
    begin {
        Write-CloudVizLog "Starting resource inventory extraction..." -Level Info
        
        # Ensure output directory exists
        if (-not (Test-Path $Script:CloudVizConfig.OutputPath)) {
            New-Item -Path $Script:CloudVizConfig.OutputPath -ItemType Directory -Force | Out-Null
        }
        
        # Set subscription context if specified
        if ($SubscriptionId) {
            try {
                Set-AzContext -SubscriptionId $SubscriptionId | Out-Null
                Write-CloudVizLog "Set context to subscription: $SubscriptionId" -Level Info
            }
            catch {
                throw "Failed to set subscription context: $($_.Exception.Message)"
            }
        }
    }
    
    process {
        try {
            $allResources = @()
            
            # Build resource query parameters
            $resourceParams = @{}
            if ($ResourceGroupName) { $resourceParams.ResourceGroupName = $ResourceGroupName }
            if ($ResourceType) { $resourceParams.ResourceType = $ResourceType }
            
            Write-CloudVizLog "Querying Azure resources..." -Level Info
            
            if ($Parallel -and $Script:CloudVizConfig.MaxConcurrentJobs -gt 1) {
                $allResources = Get-CloudVizResourcesParallel @resourceParams
            } else {
                $allResources = Get-AzResource @resourceParams
            }
            
            Write-CloudVizLog "Found $($allResources.Count) resources" -Level Info
            
            # Filter by tags if specified
            if ($Tag) {
                $allResources = $allResources | Where-Object {
                    $resource = $_
                    $matchesAllTags = $true
                    foreach ($tagKey in $Tag.Keys) {
                        if (-not $resource.Tags[$tagKey] -or $resource.Tags[$tagKey] -ne $Tag[$tagKey]) {
                            $matchesAllTags = $false
                            break
                        }
                    }
                    $matchesAllTags
                }
                Write-CloudVizLog "Filtered to $($allResources.Count) resources matching tags" -Level Info
            }
            
            # Filter preview resources if not included
            if (-not $IncludePreview) {
                $allResources = $allResources | Where-Object { 
                    $_.ResourceType -notlike "*preview*" -and $_.ResourceType -notlike "*beta*" 
                }
            }
            
            # Enrich resources with additional details
            $enrichedResources = @()
            $progressCounter = 0
            
            foreach ($resource in $allResources) {
                $progressCounter++
                $percentComplete = [math]::Round(($progressCounter / $allResources.Count) * 100, 1)
                Write-Progress -Activity "Enriching resource data" -Status "Processing $($resource.Name)" -PercentComplete $percentComplete
                
                try {
                    $enrichedResource = Get-CloudVizResourceDetails -Resource $resource
                    $enrichedResources += $enrichedResource
                }
                catch {
                    Write-CloudVizLog "Failed to enrich resource $($resource.Name): $($_.Exception.Message)" -Level Warning
                    $enrichedResources += $resource
                }
            }
            
            Write-Progress -Activity "Enriching resource data" -Completed
            
            # Create inventory object
            $inventory = [PSCustomObject]@{
                ExtractedAt = Get-Date -Format "o"
                SubscriptionId = (Get-AzContext).Subscription.Id
                SubscriptionName = (Get-AzContext).Subscription.Name
                ResourceGroupName = $ResourceGroupName
                ResourceCount = $enrichedResources.Count
                Resources = $enrichedResources
                Metadata = @{
                    Extractor = "CloudVizLegacy"
                    Version = "1.0.0"
                    Parameters = @{
                        SubscriptionId = $SubscriptionId
                        ResourceGroupName = $ResourceGroupName
                        ResourceType = $ResourceType
                        Tag = $Tag
                        IncludePreview = $IncludePreview.IsPresent
                        Parallel = $Parallel.IsPresent
                    }
                }
            }
            
            Write-CloudVizLog "Resource inventory completed: $($enrichedResources.Count) resources" -Level Info
            return $inventory
        }
        catch {
            Write-CloudVizLog "Resource inventory failed: $($_.Exception.Message)" -Level Error
            throw
        }
    }
}

function Get-CloudVizResourceDetails {
    <#
    .SYNOPSIS
    Get detailed information for a single resource
    
    .PARAMETER Resource
    Azure resource object
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Resource
    )
    
    try {
        # Get detailed resource information
        $detailedResource = Get-AzResource -ResourceId $Resource.ResourceId
        
        # Add CloudViz-specific metadata
        $detailedResource | Add-Member -NotePropertyName CloudVizMetadata -NotePropertyValue @{
            Category = $Script:ResourceTypeMap[$Resource.ResourceType].Category
            Icon = $Script:ResourceTypeMap[$Resource.ResourceType].Icon
            Color = $Script:ResourceTypeMap[$Resource.ResourceType].Color
            ExtractedAt = Get-Date -Format "o"
        } -Force
        
        # Add cost information if available
        if ($Resource.Tags) {
            $detailedResource | Add-Member -NotePropertyName CostInformation -NotePropertyValue @{
                CostCenter = $Resource.Tags["CostCenter"]
                Project = $Resource.Tags["Project"]
                Environment = $Resource.Tags["Environment"]
                Owner = $Resource.Tags["Owner"]
            } -Force
        }
        
        return $detailedResource
    }
    catch {
        Write-CloudVizLog "Failed to get details for resource $($Resource.Name): $($_.Exception.Message)" -Level Warning
        return $Resource
    }
}

function Get-CloudVizResourcesParallel {
    <#
    .SYNOPSIS
    Get resources using parallel processing
    
    .PARAMETER ResourceGroupName
    Resource group name filter
    
    .PARAMETER ResourceType
    Resource type filter
    #>
    [CmdletBinding()]
    param(
        [string]$ResourceGroupName,
        [string[]]$ResourceType
    )
    
    try {
        Write-CloudVizLog "Using parallel resource extraction..." -Level Info
        
        # Get all resource groups if not specified
        if ($ResourceGroupName) {
            $resourceGroups = @(Get-AzResourceGroup -Name $ResourceGroupName)
        } else {
            $resourceGroups = Get-AzResourceGroup
        }
        
        # Create parallel jobs for each resource group
        $jobs = @()
        foreach ($rg in $resourceGroups) {
            $scriptBlock = {
                param($rgName, $resourceTypes)
                Import-Module Az.Resources -Force
                $params = @{ ResourceGroupName = $rgName }
                if ($resourceTypes) { $params.ResourceType = $resourceTypes }
                Get-AzResource @params
            }
            
            $job = Start-Job -ScriptBlock $scriptBlock -ArgumentList $rg.ResourceGroupName, $ResourceType
            $jobs += $job
        }
        
        # Wait for jobs to complete
        $allResources = @()
        $completedJobs = 0
        
        do {
            $finishedJobs = $jobs | Where-Object { $_.State -eq 'Completed' }
            foreach ($job in $finishedJobs) {
                if ($job.Id -notin $processedJobIds) {
                    $allResources += Receive-Job -Job $job
                    Remove-Job -Job $job
                    $completedJobs++
                    $processedJobIds += $job.Id
                }
            }
            
            Start-Sleep -Milliseconds 500
            $percentComplete = [math]::Round(($completedJobs / $jobs.Count) * 100, 1)
            Write-Progress -Activity "Parallel resource extraction" -Status "Completed $completedJobs of $($jobs.Count) jobs" -PercentComplete $percentComplete
            
        } while ($completedJobs -lt $jobs.Count)
        
        Write-Progress -Activity "Parallel resource extraction" -Completed
        
        # Clean up any remaining jobs
        $jobs | Where-Object { $_.State -ne 'Completed' } | Remove-Job -Force
        
        Write-CloudVizLog "Parallel extraction completed: $($allResources.Count) resources" -Level Info
        return $allResources
    }
    catch {
        Write-CloudVizLog "Parallel extraction failed: $($_.Exception.Message)" -Level Error
        throw
    }
}

#endregion

#region Relationship Discovery

function Get-CloudVizResourceRelationships {
    <#
    .SYNOPSIS
    Discover relationships between Azure resources
    
    .DESCRIPTION
    Analyzes resource configurations to identify dependencies and relationships
    
    .PARAMETER Resources
    Array of Azure resources to analyze
    
    .PARAMETER IncludeNetworkRelationships
    Include network connectivity relationships
    
    .PARAMETER IncludeDependencies
    Include resource dependencies
    
    .EXAMPLE
    $inventory = Get-CloudVizResourceInventory
    $relationships = Get-CloudVizResourceRelationships -Resources $inventory.Resources
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [array]$Resources,
        
        [switch]$IncludeNetworkRelationships = $true,
        [switch]$IncludeDependencies = $true
    )
    
    Write-CloudVizLog "Discovering resource relationships..." -Level Info
    
    $relationships = @()
    $resourceLookup = @{}
    
    # Build resource lookup table
    foreach ($resource in $Resources) {
        $resourceLookup[$resource.ResourceId] = $resource
    }
    
    foreach ($resource in $Resources) {
        Write-CloudVizLog "Analyzing relationships for: $($resource.Name)" -Level Debug
        
        # Resource Group containment
        $rgRelationships = Get-ResourceGroupRelationships -Resource $resource -ResourceLookup $resourceLookup
        $relationships += $rgRelationships
        
        # Network relationships
        if ($IncludeNetworkRelationships) {
            $networkRelationships = Get-NetworkRelationships -Resource $resource -ResourceLookup $resourceLookup
            $relationships += $networkRelationships
        }
        
        # Dependency relationships
        if ($IncludeDependencies) {
            $dependencyRelationships = Get-DependencyRelationships -Resource $resource -ResourceLookup $resourceLookup
            $relationships += $dependencyRelationships
        }
    }
    
    # Remove duplicates
    $uniqueRelationships = $relationships | Sort-Object -Property @{Expression={$_.SourceId + $_.TargetId + $_.Type}} -Unique
    
    Write-CloudVizLog "Discovered $($uniqueRelationships.Count) unique relationships" -Level Info
    return $uniqueRelationships
}

function Get-ResourceGroupRelationships {
    <#
    .SYNOPSIS
    Get resource group containment relationships
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Resource,
        
        [Parameter(Mandatory)]
        [hashtable]$ResourceLookup
    )
    
    $relationships = @()
    
    # Find parent resource group
    $rgId = "/subscriptions/$($Resource.SubscriptionId)/resourceGroups/$($Resource.ResourceGroupName)"
    if ($ResourceLookup.ContainsKey($rgId)) {
        $relationships += [PSCustomObject]@{
            SourceId = $rgId
            TargetId = $Resource.ResourceId
            Type = 'Contains'
            Properties = @{ RelationshipType = 'ResourceGroupContainment' }
        }
    }
    
    return $relationships
}

function Get-NetworkRelationships {
    <#
    .SYNOPSIS
    Get network-related relationships
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Resource,
        
        [Parameter(Mandatory)]
        [hashtable]$ResourceLookup
    )
    
    $relationships = @()
    
    # Virtual Network relationships
    if ($Resource.ResourceType -eq 'Microsoft.Network/virtualNetworks') {
        # VNet contains subnets
        $subnets = $ResourceLookup.Values | Where-Object { 
            $_.ResourceType -eq 'Microsoft.Network/virtualNetworks/subnets' -and 
            $_.ResourceId -like "$($Resource.ResourceId)/subnets/*" 
        }
        
        foreach ($subnet in $subnets) {
            $relationships += [PSCustomObject]@{
                SourceId = $Resource.ResourceId
                TargetId = $subnet.ResourceId
                Type = 'Contains'
                Properties = @{ RelationshipType = 'NetworkContainment' }
            }
        }
    }
    
    # Network Interface relationships
    if ($Resource.ResourceType -eq 'Microsoft.Network/networkInterfaces') {
        # NICs connect to subnets and VMs
        if ($Resource.Properties -and $Resource.Properties.ipConfigurations) {
            foreach ($ipConfig in $Resource.Properties.ipConfigurations) {
                if ($ipConfig.subnet -and $ipConfig.subnet.id) {
                    if ($ResourceLookup.ContainsKey($ipConfig.subnet.id)) {
                        $relationships += [PSCustomObject]@{
                            SourceId = $Resource.ResourceId
                            TargetId = $ipConfig.subnet.id
                            Type = 'ConnectsTo'
                            Properties = @{ RelationshipType = 'NetworkConnection' }
                        }
                    }
                }
            }
        }
    }
    
    return $relationships
}

function Get-DependencyRelationships {
    <#
    .SYNOPSIS
    Get resource dependency relationships
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Resource,
        
        [Parameter(Mandatory)]
        [hashtable]$ResourceLookup
    )
    
    $relationships = @()
    
    # Find dependencies in resource properties
    if ($Resource.Properties) {
        $dependencyIds = Find-ResourceIdReferences -Properties $Resource.Properties
        
        foreach ($depId in $dependencyIds) {
            if ($ResourceLookup.ContainsKey($depId) -and $depId -ne $Resource.ResourceId) {
                $relationships += [PSCustomObject]@{
                    SourceId = $Resource.ResourceId
                    TargetId = $depId
                    Type = 'DependsOn'
                    Properties = @{ RelationshipType = 'ResourceDependency' }
                }
            }
        }
    }
    
    return $relationships
}

function Find-ResourceIdReferences {
    <#
    .SYNOPSIS
    Find Azure resource ID references in properties
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Properties
    )
    
    $resourceIds = @()
    $resourceIdPattern = '/subscriptions/[^/]+/resourceGroups/[^/]+/providers/[^/]+/[^/]+/[^/]+'
    
    function Search-Object($obj, $path = "") {
        if ($obj -is [string] -and $obj -match $resourceIdPattern) {
            $resourceIds += $obj
        }
        elseif ($obj -is [hashtable] -or $obj -is [PSCustomObject]) {
            foreach ($key in $obj.PSObject.Properties.Name) {
                Search-Object $obj.$key "$path.$key"
            }
        }
        elseif ($obj -is [array]) {
            for ($i = 0; $i -lt $obj.Count; $i++) {
                Search-Object $obj[$i] "$path[$i]"
            }
        }
    }
    
    Search-Object $Properties
    return $resourceIds | Select-Object -Unique
}

#endregion

#region Data Export/Import

function Export-CloudVizResourceData {
    <#
    .SYNOPSIS
    Export resource inventory to file
    
    .DESCRIPTION
    Exports CloudViz resource inventory to JSON, CSV, or other formats
    
    .PARAMETER Inventory
    Resource inventory object
    
    .PARAMETER OutputPath
    Output file path
    
    .PARAMETER Format
    Export format (JSON, CSV, XML)
    
    .EXAMPLE
    $inventory = Get-CloudVizResourceInventory
    Export-CloudVizResourceData -Inventory $inventory -OutputPath "resources.json" -Format JSON
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Inventory,
        
        [Parameter(Mandatory)]
        [string]$OutputPath,
        
        [ValidateSet('JSON', 'CSV', 'XML')]
        [string]$Format = 'JSON'
    )
    
    try {
        Write-CloudVizLog "Exporting resource data to: $OutputPath" -Level Info
        
        switch ($Format) {
            'JSON' {
                $Inventory | ConvertTo-Json -Depth 20 | Out-File -FilePath $OutputPath -Encoding UTF8
            }
            'CSV' {
                $Inventory.Resources | Export-Csv -Path $OutputPath -NoTypeInformation
            }
            'XML' {
                $Inventory | Export-Clixml -Path $OutputPath
            }
        }
        
        Write-CloudVizLog "Export completed successfully" -Level Info
    }
    catch {
        Write-CloudVizLog "Export failed: $($_.Exception.Message)" -Level Error
        throw
    }
}

function Import-CloudVizResourceData {
    <#
    .SYNOPSIS
    Import resource inventory from file
    
    .DESCRIPTION
    Imports CloudViz resource inventory from previously exported file
    
    .PARAMETER FilePath
    Input file path
    
    .PARAMETER Format
    Import format (JSON, XML)
    
    .EXAMPLE
    $inventory = Import-CloudVizResourceData -FilePath "resources.json" -Format JSON
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$FilePath,
        
        [ValidateSet('JSON', 'XML')]
        [string]$Format = 'JSON'
    )
    
    try {
        Write-CloudVizLog "Importing resource data from: $FilePath" -Level Info
        
        if (-not (Test-Path $FilePath)) {
            throw "File not found: $FilePath"
        }
        
        switch ($Format) {
            'JSON' {
                $inventory = Get-Content -Path $FilePath -Raw | ConvertFrom-Json
            }
            'XML' {
                $inventory = Import-Clixml -Path $FilePath
            }
        }
        
        Write-CloudVizLog "Import completed: $($inventory.ResourceCount) resources" -Level Info
        return $inventory
    }
    catch {
        Write-CloudVizLog "Import failed: $($_.Exception.Message)" -Level Error
        throw
    }
}

#endregion

#region Aliases for backward compatibility

# Legacy AzViz aliases
Set-Alias -Name Get-AzVizResourceInventory -Value Get-CloudVizResourceInventory
Set-Alias -Name Export-AzVizDiagram -Value Export-CloudVizDiagram
Set-Alias -Name cloudviz -Value Get-CloudVizResourceInventory

#endregion

# Module initialization
Write-CloudVizLog "CloudViz Legacy PowerShell module loaded successfully" -Level Info
Write-CloudVizLog "For help, run: Get-Help Get-CloudVizResourceInventory -Full" -Level Info
