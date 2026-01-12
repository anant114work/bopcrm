function loadCallRecords() {
    const tbody = document.getElementById('callRecordsTable');
    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 20px;"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>';
    
    fetch('/call-analytics/api/')
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Call analytics data:', data);
        tbody.innerHTML = '';
        
        if (data.success && data.calls && data.calls.length > 0) {
            data.calls.forEach(call => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>
                        <div style="font-size: 12px; font-weight: 500;">${formatDate(call.start_time)}</div>
                        <div style="font-size: 10px; color: #6b7280;">${formatTime(call.start_time)}</div>
                    </td>
                    <td>
                        <div style="font-weight: 600; margin-bottom: 2px;">${call.customer_number || 'Unknown'}</div>
                        <div style="font-size: 10px; color: #6b7280;">Tata IVR</div>
                    </td>
                    <td>
                        <div style="font-size: 12px;">${call.agent_name || 'System'}</div>
                        <div style="font-size: 10px; color: #6b7280;">${call.department || 'General'}</div>
                    </td>
                    <td>${call.duration ? formatDuration(call.duration) : '0s'}</td>
                    <td>
                        <span class="status-badge status-${call.status || 'unknown'}">
                            ${(call.status || 'Unknown').charAt(0).toUpperCase() + (call.status || 'unknown').slice(1)}
                        </span>
                    </td>
                    <td>
                        ${call.recording_url ? 
                            '<button class="btn-play" onclick="playRecording(\'' + call.recording_url + '\')">Play</button>' : 
                            '<span style="color: #6b7280; font-size: 10px;">No recording</span>'
                        }
                    </td>
                    <td>
                        <button class="btn-details" onclick="viewCallDetails('${call.customer_number}')">Details</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
            
            // Add summary row
            const summaryRow = document.createElement('tr');
            summaryRow.innerHTML = `
                <td colspan="7" style="text-align: center; padding: 10px; background: #f8fafc; color: #10b981; font-size: 12px;">
                    <i class="fas fa-check-circle"></i> Showing ${data.calls.length} recent calls from Tata IVR
                </td>
            `;
            tbody.appendChild(summaryRow);
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align: center; padding: 20px; color: #6b7280;">
                        <div style="font-size: 14px; margin-bottom: 8px;"><i class="fas fa-info-circle"></i> No call records found</div>
                        <div style="font-size: 12px;">Tata IVR integration is connected but no calls available for today</div>
                    </td>
                </tr>
            `;
        }
    })
    .catch(error => {
        console.error('Error loading call records:', error);
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 20px; color: #ef4444;">
                    <div style="font-size: 14px; margin-bottom: 8px;"><i class="fas fa-exclamation-triangle"></i> Error Loading Call Records</div>
                    <div style="font-size: 12px;">Error: ${error.message}</div>
                    <div style="margin-top: 8px;"><button class="btn-tata" onclick="loadCallRecords()">Retry</button></div>
                </td>
            </tr>
        `;
    });
}