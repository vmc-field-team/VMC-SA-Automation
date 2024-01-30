#docker run -i --entrypoint=/usr/bin/pwsh -w /tmp/scripts/skyler/Active-Directory -v /hank/scripts/hank:/tmp/scripts m>

#Must run on dc01 (domain controller) to make this run
$secpwd = convertto-securestring -asplaintext -force -string ""
$Credentials = new-object system.management.automation.pscredential "set\administrator",$secpwd
$session = New-PSSession -ComputerName 10.34.0.2 -Credential $Credentials -Authentication Negotiate -ErrorAction Ignore
# $results = Import-module -PSSession $session -Name ActiveDirectory
echo $pwd
$data = get-content "\tmp\scripts\Active-Directory\workshopuser.csv" | ConvertFrom-Csv
foreach ($i in $data)
{
    write-host "Gathering info from" $i.Name $i.Handle
    #add user to AD
    #$region = $i.Region
    $results = Invoke-Command -Session $session -ArgumentList $i.name,$i.handle -ScriptBlock {
        $name = $args[0]
        $handle = $args[1]
        $secUserPwd = convertto-securestring -asplaintext -force -string ""
        New-ADUser -Name $name -SamAccountName $handle -UserPrincipalName "$handle@set.local" -Path "OU=WorkshopUser,O>
        Set-ADUser -Identity $handle -ChangePasswordAtLogon:$FALSE
    }
    $results
}