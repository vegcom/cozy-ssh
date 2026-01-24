$UserName = "$env:COMPUTERNAME\$env:USERNAME"
$SshRoot  = "$HOME\.ssh"

$PrivateKeyNames = @("id_rsa","id_dsa","id_ecdsa","id_ed25519", "git")
$StrictFiles = @("authorized_keys","config")
$StrictDirectories = @("ssh_config.d","known_hosts")

function Set-DirectoryPerms {
    param([string]$Path)
    $acl = Get-Acl $Path
    $acl.SetAccessRuleProtection($true, $false)
    $acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) }
    $acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule($UserName,"FullControl","ContainerInherit,ObjectInherit","None","Allow")))
    $acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule("NT AUTHORITY\SYSTEM","FullControl","ContainerInherit,ObjectInherit","None","Allow")))
    $acl.SetOwner([System.Security.Principal.NTAccount]$UserName)
    Set-Acl -Path $Path -AclObject $acl
}

function Set-NormalFilePerms {
    param([string]$Path)
    $item = Get-Item $Path
    if ($item.Attributes -match "ReadOnly") {
        Set-ItemProperty $Path -Name Attributes -Value Normal
    }
    $acl = Get-Acl $Path
    $acl.SetAccessRuleProtection($true, $false)
    $acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) }
    $acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule($UserName,"FullControl","Allow")))
    $acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule("NT AUTHORITY\SYSTEM","FullControl","Allow")))
    $acl.SetOwner([System.Security.Principal.NTAccount]$UserName)
    Set-Acl -Path $Path -AclObject $acl
}

function Set-StrictFilePerms {
    param([string]$Path)
    $item = Get-Item $Path
    if ($item.Attributes -match "ReadOnly") {
        Set-ItemProperty $Path -Name Attributes -Value Normal
    }
    $acl = Get-Acl $Path
    $acl.SetAccessRuleProtection($true, $false)
    $acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) }
    $acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule($UserName,"FullControl","Allow")))
    $acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule("NT AUTHORITY\SYSTEM","FullControl","Allow")))
    $acl.SetOwner([System.Security.Principal.NTAccount]$UserName)
    Set-Acl -Path $Path -AclObject $acl
}

Set-DirectoryPerms $SshRoot

Get-ChildItem $SshRoot -Recurse -Force | ForEach-Object {
    if ($_.PSIsContainer) {
        Set-DirectoryPerms $_.FullName
        return
    }

    $name   = $_.Name
    $parent = Split-Path $_.FullName -Leaf

    if ($PrivateKeyNames -contains $name) { Set-StrictFilePerms $_.FullName; return }
    if ($name -like "*.pub") { Set-NormalFilePerms $_.FullName; return }
    if ($StrictFiles -contains $name) { Set-StrictFilePerms $_.FullName; return }
    if ($StrictDirectories -contains $parent) { Set-StrictFilePerms $_.FullName; return }

    Set-NormalFilePerms $_.FullName
}
