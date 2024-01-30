#configure CloudManagement Workshop SDDCs
# Thomas Sauerer
# Updated: 01/13/2022


# Datastore where VMs will be created
#(Should not need changed for VMware Cloud on AWS)
$ds = "WorkloadDatastore"

# Gather data from workshop json
#$data += get-content "json\vmcexpert1.json" | ConvertFrom-Json
$data += get-content "json\vmcexpert2.json" | ConvertFrom-Json
#$data += get-content "json\vmcexpert3.json" | ConvertFrom-Json

# For each to gather all necessary infos
foreach ($i in $data) {
    # if ($i.sddcName -eq $WSDDCName) {
        write-host "Gathering info from" $i.OrgName
        $global:OrgName = $i.orgName
        $global:RefreshToken = $i.RefreshToken
        foreach ($s in $i.sddcConfig) {
          $sddcName = $s.SDDCName

              #Connect-VMC to get vCenter creds
              $vmcconnect = Connect-VmcServer -RefreshToken $RefreshToken

              #Connect to NSX-t Proxy
              Connect-NSXTProxy -RefreshToken $RefreshToken -OrgName $OrgName -SDDCName $sddcName #-Verbose

              ###### Create groups ######

              #Create Group "RFC1918" CGW
              $results = Get-NSXTGroup -Name "RFC1918" -GatewayType "CGW"
                if ($results.name -eq $null) {
                    $nsxtResults = New-NSXTGroup -GatewayType CGW -Name RFC1918 -IPAddress @("192.168.0.0/16", "172.16.0.0/12", "10.0.0.0/8")
                }
                else {
                    Write-Host -ForegroundColor Yellow "Skipping mgw Group already exists"
                }

              #Create Group "RFC1918" MGW
              $results = Get-NSXTGroup -Name "RFC1918" -GatewayType "MGW"
                if ($results.name -eq $null) {
                    $nsxtResults = New-NSXTGroup -GatewayType MGW -Name RFC1918 -IPAddress @("192.168.0.0/16", "172.16.0.0/12", "10.0.0.0/8")
                }
                else {
                    Write-Host -ForegroundColor Yellow "Skipping mgw Group already exists"
                }

              #Create Group "Jumphost" MGW
              $results = Get-NSXTGroup -Name "Jumphost" -GatewayType "MGW"
                if ($results.name -eq $null) {
                    $nsxtResults = New-NSXTGroup -GatewayType MGW -Name Jumphost -IPAddress @("54.221.112.34", "80.132.117.173","44.205.219.118")
                }
                else {
                    Write-Host -ForegroundColor Yellow "Skipping mgw Group already exists"
                }

              ###### Create MGW Firewall Rules ######

              #create firewall rule to access vCenter from CGW
              $results = Get-NSXTFirewall -Name "Inbound-vCenter" -GatewayType "MGW"
                if ($results.name -eq $null) {
                    $nsxtResults = New-NSXTFirewall -name "Inbound-vCenter" -GatewayType "MGW" -SequenceNumber 1 -SourceGroup "RFC1918" -DestinationGroup "vCenter" -Service "HTTPS" -Action "ALLOW"# -Scope "All"#-Troubleshoot $true
                }
                else {
                    Write-Host -ForegroundColor Yellow "Skipping MGW firewall already exists"
                }

              #create firewall rule to access vCenter from Jumphost
              $results = Get-NSXTFirewall -Name "Inbound-vCenter-Jumphost" -GatewayType "MGW"
                if ($results.name -eq $null) {
                    $nsxtResults = New-NSXTFirewall -name "Inbound-vCenter-Jumphost" -GatewayType "MGW" -SequenceNumber 2 -SourceGroup "Jumphost" -DestinationGroup "vCenter" -Service "HTTPS" -Action "ALLOW"# -Scope "All"#-Troubleshoot $true
                }
                else {
                    Write-Host -ForegroundColor Yellow "Skipping MGW firewall already exists"
                }

              #create firewall rule to access ESXi from CGW
              $results = Get-NSXTFirewall -Name "Inbound-ESXi" -GatewayType "MGW"
                if ($results.name -eq $null) {
                    $nsxtResults = New-NSXTFirewall -name "Inbound-ESXi" -GatewayType "MGW" -SequenceNumber 2 -SourceGroup "RFC1918" -DestinationGroup "ESXi" -Service "HTTPS" -Action "ALLOW"# -Scope "All"#-Troubleshoot $true
                }
                else {
                    Write-Host -ForegroundColor Yellow "Skipping MGW firewall already exists"
                }

              #create firewall rule to access NSX-Manager from CGW
              $results = Get-NSXTFirewall -Name "Inbound-NSX-Manager" -GatewayType "MGW"
                if ($results.name -eq $null) {
                    $nsxtResults = New-NSXTFirewall -name "Inbound-NSX-Manager" -GatewayType "MGW" -SequenceNumber 2 -SourceGroup "RFC1918" -DestinationGroup "NSX Manager" -Service "HTTPS" -Action "ALLOW"# -Scope "All"#-Troubleshoot $true
                }
                else {
                    Write-Host -ForegroundColor Yellow "Skipping MGW firewall already exists"
                }

              ###### Create CGW Firewall Rules ######

              # RFC1918 to RFC1918
              $results = Get-NSXTFirewall -Name "Internal-Communication" -GatewayType "CGW"
                if ($results.name -eq $null) {
                    $nsxtResults = New-NSXTFirewall -Name "Internal-Communication" -GatewayType "CGW" -SourceGroup "ANY" -DestinationGroup "ANY" -Service "ANY" -Logged $false -SequenceNumber 3 -Action "ALLOW" -InfraScope "All Uplinks"
                }
                else {
                    Write-Host -ForegroundColor Yellow "Skipping CGW firewall already exists"
                }

              #Internet Access 443
              $results = Get-NSXTFirewall -Name "Internet-Communication" -GatewayType "CGW"
                if ($results.name -eq $null) {
                    $nsxtResults = New-NSXTFirewall -Name "Internet-Communication" -GatewayType "CGW" -SourceGroup "RFC1918" -DestinationGroup "ANY" -Service "HTTPS" -Logged $false -SequenceNumber 3 -Action "ALLOW" -InfraScope "Internet Interface"
                }
                else {
                    Write-Host -ForegroundColor Yellow "Skipping CGW firewall already exists"
                }

              #Done with the NSX-T Firewall Rules
              #If the execusion of the script fails to connect to the vcenter, make sure the public IP is added to the "Jumphost" MGW Group

              #get creds
              write-host $orgName $sddcName
              $sddcCreds = Get-VMCSDDCDefaultCredential -Org $orgName -sddc $sddcName
              $vCenter = $sddcCreds.vc_public_ip
              $vCenterUser = $sddcCreds.cloud_username
              $vCenterUserPassword = $sddcCreds.cloud_password

              #ignore cert
              set-PowerCLIConfiguration -InvalidCertificateAction Ignore -confirm:$false
              write-host "Establishing connection to $vCenter" -foreground green
              $results = Connect-viserver $vCenter -user $vCenterUser -password $vCenterUserPassword -WarningAction 0
              $results = Get-ContentLibraryItem -Name vmc-content-library -EA SilentlyContinue
              if ($results.ContentLibrary -eq $null) {
                  #connect to cis server
                  $results = Connect-cisserver $vCenter -user $vCenterUser -password $vCenterUserPassword -WarningAction 0
                    Write-Host $vCenter $vCenterUser $vCenterUserPassword
                  $datastoreID = (Get-Datastore -Name $ds).extensiondata.moref.value
                  # Create a Subscribed content library on an existing datastore
                  $ContentCatalog = Get-CisService -Name "com.vmware.content.subscribed_library"
                  $createSpec = $ContentCatalog.help.create.create_spec.Create()
                  $createSpec.subscription_info.authentication_method = "NONE"
                  $createSpec.subscription_info.ssl_thumbprint = "e2:00:79:ce:5d:d4:ad:21:09:df:92:6e:64:a4:62:2a:26:66:ff:cc"
                  $createSpec.subscription_info.automatic_sync_enabled = $true
                  $createSpec.subscription_info.subscription_url = "http://vmc-elw-cmworkshop-west-1.s3.us-west-1.amazonaws.com/lib.json" # create a link for each profile '{Profile}-{Region}-vms.s3.{Region}.amazonaws.com/lib.json'
                  $createSpec.subscription_info.on_demand = $false
                  $createSpec.subscription_info.password = $null
                  $createSpec.server_guid = $null
                  $createspec.name = "vmc-content-library"
                  $createSpec.description = "workshop templates"
                  $createSpec.type = "SUBSCRIBED"
                  $createSpec.publish_info = $null
                  $datastoreID = [VMware.VimAutomation.Cis.Core.Types.V1.ID]$datastoreID
                  $StorageSpec = New-Object PSObject -Property @{
                      datastore_id = $datastoreID
                      type         = "DATASTORE"
                  }
                  $CreateSpec.storage_backings.Add($StorageSpec)
                  $UniqueID = [guid]::NewGuid().tostring()
                  $ContentCatalog.create($UniqueID, $createspec)

                  ##### disconnect to CIS-, Vi- & VMC-server #####
                  Disconnect-cisserver $vCenter -Confirm:$false
                  Disconnect-viserver -Server $vCenter -Confirm:$false
                  Disconnect-Vmc -Server $vmcconnect -Confirm:$false
              }
              else {
                  Write-Host -ForegroundColor Yellow "Skipping content library already exists"
              }
          }
      }
