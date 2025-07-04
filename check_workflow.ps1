param(
    [string]$Owner = "Rahuljoshi07",
    [string]$Repo = "job-bot"
)

try {
    Write-Host "Checking GitHub Actions workflow status for $Owner/$Repo..." -ForegroundColor Green
    Write-Host ""
    
    # Get workflow runs
    $uri = "https://api.github.com/repos/$Owner/$Repo/actions/runs"
    $response = Invoke-RestMethod -Uri $uri -Headers @{
        'Accept' = 'application/vnd.github.v3+json'
        'User-Agent' = 'PowerShell-Script'
    }
    
    Write-Host "Total workflow runs: $($response.total_count)" -ForegroundColor Cyan
    Write-Host ""
    
    if ($response.workflow_runs.Count -gt 0) {
        Write-Host "Latest 5 workflow runs:" -ForegroundColor Yellow
        Write-Host ("=" * 50)
        
        $response.workflow_runs | Select-Object -First 5 | ForEach-Object {
            Write-Host "Run ID: $($_.id)" -ForegroundColor White
            Write-Host "Name: $($_.name)" -ForegroundColor White
            Write-Host "Status: $($_.status)" -ForegroundColor $(if ($_.status -eq "completed") {"Green"} else {"Yellow"})
            Write-Host "Conclusion: $($_.conclusion)" -ForegroundColor $(if ($_.conclusion -eq "success") {"Green"} elseif ($_.conclusion -eq "failure") {"Red"} else {"Yellow"})
            Write-Host "Branch: $($_.head_branch)" -ForegroundColor Gray
            Write-Host "Created: $($_.created_at)" -ForegroundColor Gray
            Write-Host "Updated: $($_.updated_at)" -ForegroundColor Gray
            Write-Host "URL: $($_.html_url)" -ForegroundColor Blue
            Write-Host ("-" * 30)
        }
    } else {
        Write-Host "No workflow runs found." -ForegroundColor Red
    }
    
    # Get workflows
    Write-Host ""
    Write-Host "Available workflows:" -ForegroundColor Yellow
    $workflowUri = "https://api.github.com/repos/$Owner/$Repo/actions/workflows"
    $workflows = Invoke-RestMethod -Uri $workflowUri -Headers @{
        'Accept' = 'application/vnd.github.v3+json'
        'User-Agent' = 'PowerShell-Script'
    }
    
    $workflows.workflows | ForEach-Object {
        Write-Host "- $($_.name) ($($_.state))" -ForegroundColor Cyan
        Write-Host "  Path: $($_.path)" -ForegroundColor Gray
        Write-Host "  Badge: $($_.badge_url)" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure the repository exists and is public, or you have proper authentication." -ForegroundColor Yellow
}
