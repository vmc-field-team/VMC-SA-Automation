
$secUserPwd = convertto-securestring -asplaintext -force -string ""

#Must run on dc03 (domain controller) to make this run
$secpwd = convertto-securestring -asplaintext -force -string "" 
$Credentials = new-object system.management.automation.pscredential "set\bender",$secpwd
$session = New-PSSession -ComputerName dc01 -Credential $Credentials -ErrorAction Ignore
$results = Import-module -PSSession $session -Name ActiveDirectory


$data = get-content ".\sme-emea.csv" | ConvertFrom-Csv
foreach ($i in $data)
{
    write-host "Gathering info from" $i.Region $i.Name $i.Handle
    #add user to AD
    $handle = $i.Handle
    $region = $i.Region
    try {
        New-ADUser -Name $name -SamAccountName $handle -UserPrincipalName "$handle@set.local" -Path "OU=Users,OU=$region,DC=set,DC=local" -AccountPassword $secUserPwd -Enabled $true -ErrorAction Stop
        write-host "Account created successfully"
    }
    catch {
        write-host $_.Exception.Message -ForegroundColor Yellow
    }
    try {
        Set-ADUser -Identity $handle -ChangePasswordAtLogon:$TRUE
        write-host "Password changed successfully"
    }
    catch {
        write-host $_.Exception.Message -ForegroundColor Yellow
    }
    
    #-GivenName $AD_name -Surname $AD_name
    #$groupName = $region.replace(" ","_")
    Try {
        $result = Add-ADGroupMember -Identity "Horizon $region" -Members $handle
        write-host "Account added to group successfully"
    }
    catch {
        write-host $_.Exception.Message -ForegroundColor Yellow
    }
}
