Param (
    [Parameter(Mandatory=$true)][String]$handle
)
$secpwd = convertto-securestring -asplaintext -force -string "" 
$Credentials = new-object system.management.automation.pscredential "set\administrator",$secpwd
$session = New-PSSession -ComputerName XX.XX.X.X -Credential $Credentials -Authentication Negotiate -ErrorAction Ignore

$results = Invoke-Command -Session $session -ArgumentList $handle -ScriptBlock {
    $handle = $args[0]  
    $secUserPwd = convertto-securestring -asplaintext -force -string ""
    Set-ADAccountPassword -Identity $handle -NewPassword $secUserPwd -Reset
    Set-ADUser -Identity $handle -ChangePasswordAtLogon $true
    Unlock-ADAccount -Identity $handle
}
$results
write-host "Your password has been successfully set to default!"
write-host "Please join our #vmc-set-demo-public Slack Channel! You will find a documentation and the default password pinned to the Channel!"