Param (
    [Parameter(Mandatory=$true)][String]$handle,
    [Parameter(Mandatory=$true)][String]$name
)
$secpwd = convertto-securestring -asplaintext -force -string "" 
$Credentials = new-object system.management.automation.pscredential "set\administrator",$secpwd
$session = New-PSSession -ComputerName 10.34.0.2 -Credential $Credentials -Authentication Negotiate

$results = Invoke-Command -Session $session -ArgumentList $handle,$name -ScriptBlock {
    $handle = $args[0]  
    $name = $args[1]
    $secUserPwd = convertto-securestring -asplaintext -force -string ""
    New-ADUser -Name $name -SamAccountName $handle -UserPrincipalName "$handle@set.local" -Path "OU=Users,OU=GlobalVMC,DC=set,DC=local" -AccountPassword $secUserPwd -Enabled $true -ErrorAction Stop
    Set-ADUser -Identity $handle -ChangePasswordAtLogon:$TRUE
    "horizon-user","vcenter-user","AWS-User" | Add-ADGroupMember -Members $handle
}
$results
write-host "Account created successfully"
write-host "Login is $handle@Domain with default password!"
write-host "Please join our # Slack Channel! You will find a documentation and the default password pinned to the Channel!"