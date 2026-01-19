// WhatsApp Campaign Management JavaScript

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateCount() {
    const count = document.querySelectorAll('.lead-checkbox:checked').length;
    document.getElementById('selectedCount').textContent = count;
    updateButtons();
}

function toggleAll() {
    const selectAll = document.getElementById('selectAllCheckbox');
    document.querySelectorAll('.lead-checkbox').forEach(cb => {
        cb.checked = selectAll.checked;
    });
    updateCount();
}

function updateButtons() {
    const selectedCount = document.querySelectorAll('.lead-checkbox:checked').length;
    const templateSelected = document.getElementById('templateSelect').value;
    const dripSelected = document.querySelector('.drip-checkbox:checked');
    
    document.getElementById('sendSingleBtn').disabled = selectedCount === 0 || !templateSelected;
    document.getElementById('sendDripBtn').disabled = selectedCount === 0 || !dripSelected;
}

function createCampaign(type) {
    const url = type === 'gaur' ? '/drip-campaigns/create-gaur-yamuna/' : '/drip-campaigns/create-spj-10day/';
    const name = type === 'gaur' ? 'Gaur Yamuna' : 'SPJ 10-Day';
    
    if (!confirm(`Create ${name} campaign?`)) return;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`${name} campaign created successfully!`);
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'Failed to create campaign'));
        }
    })
    .catch(error => {
        alert('Error: ' + error);
    });
}

function loadProjectTemplates() {
    const projectId = document.getElementById('projectSelect').value;
    const templateSelect = document.getElementById('templateSelect');
    const options = templateSelect.querySelectorAll('option');
    
    options.forEach(option => {
        if (option.value === '') {
            option.style.display = 'block';
        } else {
            const optionProject = option.getAttribute('data-project');
            option.style.display = !projectId || optionProject === projectId ? 'block' : 'none';
        }
    });
    
    templateSelect.value = '';
    updateTemplatePreview();
}

function updateTemplatePreview() {
    const select = document.getElementById('templateSelect');
    const preview = document.getElementById('templatePreview');
    const selectedOption = select.options[select.selectedIndex];
    
    if (select.value) {
        const delay = selectedOption.getAttribute('data-delay') || '0';
        preview.innerHTML = `<strong>${selectedOption.text}</strong><br><small>Delay: ${delay} minutes</small><br><br>Select this template to send messages.`;
    } else {
        preview.innerHTML = 'Select a template to see preview...';
    }
    
    updateButtons();
}

function sendSingleMessage() {
    const selectedLeads = Array.from(document.querySelectorAll('.lead-checkbox:checked')).map(cb => cb.value);
    const templateId = document.getElementById('templateSelect').value;
    
    if (selectedLeads.length === 0 || !templateId) {
        alert('Please select leads and a template');
        return;
    }
    
    if (!confirm(`Send message to ${selectedLeads.length} lead(s)?`)) return;
    
    fetch('/whatsapp/send-single/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            lead_ids: selectedLeads,
            template_id: templateId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Messages sent successfully to ${data.sent_count} leads!`);
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'Failed to send messages'));
        }
    })
    .catch(error => {
        alert('Error: ' + error);
    });
}

function startDripCampaign() {
    const selectedLeads = Array.from(document.querySelectorAll('.lead-checkbox:checked')).map(cb => cb.value);
    const campaignId = document.querySelector('.drip-checkbox:checked')?.value;
    
    if (selectedLeads.length === 0 || !campaignId) {
        alert('Please select leads and a drip campaign');
        return;
    }
    
    if (!confirm(`Start drip campaign for ${selectedLeads.length} lead(s)?`)) return;
    
    fetch('/whatsapp/start-drip/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            lead_ids: selectedLeads,
            campaign_id: campaignId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Drip campaign started for ${data.enrolled_count} leads!`);
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'Failed to start campaign'));
        }
    })
    .catch(error => {
        alert('Error: ' + error);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateCount();
    updateButtons();
});
