document.addEventListener('DOMContentLoaded', () => {
    // DOM Element references
    const dropZone = document.getElementById('drop-zone');
    const zipInput = document.getElementById('zip-input');
    const browseBtn = document.getElementById('browse-btn');
    const extractBtn = document.getElementById('extract-btn');
    const pdfList = document.getElementById('pdf-list');
    const contactsTableBody = document.getElementById('contacts-table-body');
    const contactCount = document.getElementById('contact-count');
    const selectAllBtn = document.getElementById('select-all-btn');
    const masterCheckbox = document.getElementById('master-checkbox');
    const addContactBtn = document.getElementById('add-contact-btn');
    const messageText = document.getElementById('message-text');
    const messagePreview = document.getElementById('message-preview');
    const sendBtn = document.getElementById('send-btn');
    const progressBar = document.getElementById('progress-bar');
    const liveLog = document.getElementById('live-log');

    // Stats
    const statTotal = document.getElementById('stat-total');
    const statDelivered = document.getElementById('stat-delivered');
    const statFailed = document.getElementById('stat-failed');
    const statInvalid = document.getElementById('stat-invalid');

    let extractedContacts = [];

    // Helper: Add log message
    function log(msg) {
        const p = document.createElement('p');
        p.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
        liveLog.appendChild(p);
        liveLog.scrollTop = liveLog.scrollHeight;
    }

    // Drag and Drop Upload
    browseBtn.addEventListener('click', () => zipInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-indigo-500');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('border-indigo-500');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-indigo-500');
        if (e.dataTransfer.files.length) {
            handleZipFile(e.dataTransfer.files[0]);
        }
    });

    zipInput.addEventListener('change', () => {
        if (zipInput.files.length) {
            handleZipFile(zipInput.files[0]);
        }
    });

    async function handleZipFile(file) {
        if (!file.name.endsWith('.zip')) {
            alert('Please select a valid ZIP archive.');
            return;
        }

        log(`Uploading ${file.name}...`);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/upload-zip', { method: 'POST', body: formData });
            const data = await res.json();
            if (res.ok) {
                log(`ZIP upload complete. Extracted ${data.count} PDF(s).`);
                pdfList.innerHTML = data.pdf_files.map(f => `<div class="p-2 bg-slate-900 rounded border border-slate-700/60 flex items-center gap-2"><i class="fa-solid fa-file-pdf text-rose-400"></i><span class="truncate">${f}</span></div>`).join('');
                extractBtn.disabled = false;
                extractBtn.className = "mt-4 w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 rounded-lg text-xs transition-colors flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30 cursor-pointer";
            } else {
                log(`Error: ${data.detail}`);
            }
        } catch (err) {
            log(`Upload failed: ${err.message}`);
        }
    }

    // Extract Contacts
    extractBtn.addEventListener('click', async () => {
        log('Extracting contacts from PDFs (Regex + OCR Fallback)...');
        try {
            const res = await fetch('/extract-contacts', { method: 'POST' });
            const data = await res.json();
            if (res.ok) {
                extractedContacts = data.contacts;
                log(`Extraction successful. Found ${data.total_contacts} contacts.`);
                renderContactsTable(extractedContacts);
            } else {
                log(`Error: ${data.detail}`);
            }
        } catch (err) {
            log(`Extraction failed: ${err.message}`);
        }
    });

    // Render Contacts Table
    function renderContactsTable(contacts) {
        contactCount.textContent = `${contacts.length} Contacts`;
        if (!contacts.length) {
            contactsTableBody.innerHTML = `<tr><td colspan="6" class="p-6 text-center text-slate-500 italic">No contacts found.</td></tr>`;
            return;
        }

        contactsTableBody.innerHTML = contacts.map((c, idx) => `
            <tr class="hover:bg-slate-800/80 transition-colors" data-idx="${idx}">
                <td class="p-3 text-center"><input type="checkbox" class="row-checkbox" checked></td>
                <td class="p-3 font-medium text-slate-100" contenteditable="true" data-field="name">${c.name}</td>
                <td class="p-3 ${c.confidence < 1.0 ? 'low-confidence' : 'text-slate-200'}" contenteditable="true" data-field="phone">${c.phone}</td>
                <td class="p-3 text-slate-400 truncate max-w-xs">${c.source_pdf}</td>
                <td class="p-3">
                    <span class="px-2 py-0.5 rounded text-[10px] font-semibold ${c.confidence === 1.0 ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'}">
                        ${c.confidence === 1.0 ? '100% Text' : '95% OCR'}
                    </span>
                </td>
                <td class="p-3 text-center">
                    <button class="delete-row-btn text-rose-400 hover:text-rose-300 transition-colors text-xs px-2 py-1">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        // Add Delete Event Listeners
        document.querySelectorAll('.delete-row-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tr = e.target.closest('tr');
                const idx = tr.getAttribute('data-idx');
                extractedContacts.splice(idx, 1);
                renderContactsTable(extractedContacts);
            });
        });
    }

    // Select All
    selectAllBtn.addEventListener('click', () => {
        masterCheckbox.checked = !masterCheckbox.checked;
        document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = masterCheckbox.checked);
    });

    masterCheckbox.addEventListener('change', () => {
        document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = masterCheckbox.checked);
    });

    // Add Manual Row
    addContactBtn.addEventListener('click', () => {
        extractedContacts.unshift({
            name: 'New Contact',
            phone: '+919876543210',
            source_pdf: 'manual_entry.pdf',
            confidence: 1.0,
            status: 'pending',
            is_valid: true
        });
        renderContactsTable(extractedContacts);
    });

    // Live Message Preview
    messageText.addEventListener('input', () => {
        const sampleName = extractedContacts.length > 0 ? extractedContacts[0].name : 'Contact';
        const samplePhone = extractedContacts.length > 0 ? extractedContacts[0].phone : '+91XXXXXXXXXX';
        messagePreview.textContent = messageText.value.replace(/{{name}}/g, sampleName).replace(/{{phone}}/g, samplePhone);
    });

    // Send Bulk Messages
    sendBtn.addEventListener('click', async () => {
        const rows = document.querySelectorAll('#contacts-table-body tr');
        const selectedContacts = [];

        rows.forEach((tr, idx) => {
            const cb = tr.querySelector('.row-checkbox');
            if (cb && cb.checked) {
                const nameCell = tr.querySelector('[data-field="name"]');
                const phoneCell = tr.querySelector('[data-field="phone"]');
                const sourcePdf = extractedContacts[idx] ? extractedContacts[idx].source_pdf : 'manual_entry.pdf';

                selectedContacts.push({
                    name: nameCell ? nameCell.textContent.trim() : 'Contact',
                    phone: phoneCell ? phoneCell.textContent.trim() : '',
                    source_pdf: sourcePdf,
                    status: 'pending',
                    confidence: 1.0,
                    is_valid: true
                });
            }
        });

        if (!selectedContacts.length) {
            alert('Please select at least one contact to send messages to.');
            return;
        }

        const channel = document.querySelector('.channel-radio:checked').value;
        const fast2smsKey = document.getElementById('fast2sms-key').value;

        log(`Starting bulk dispatch to ${selectedContacts.length} recipients via ${channel.toUpperCase()}...`);
        progressBar.style.width = '30%';

        const payload = {
            message: messageText.value,
            channel: channel,
            contacts: selectedContacts,
            fast2sms_api_key: fast2smsKey
        };

        try {
            const res = await fetch('/send-messages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            progressBar.style.width = '100%';

            if (res.ok) {
                log(`Dispatch complete! Delivered: ${data.delivered}, Failed: ${data.failed}, Invalid: ${data.invalid}`);
                statTotal.textContent = data.total;
                statDelivered.textContent = data.delivered;
                statFailed.textContent = data.failed;
                statInvalid.textContent = data.invalid;
            } else {
                log(`Error: ${data.detail}`);
            }
        } catch (err) {
            log(`Dispatch failed: ${err.message}`);
        }
    });
});
