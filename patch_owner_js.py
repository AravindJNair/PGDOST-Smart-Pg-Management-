import pathlib

f = pathlib.Path(r'c:\Users\aravi\OneDrive\Documents\newfinalyearproject\frontend\pages\owner-dashboard.html')
html = f.read_text(encoding='utf-8')

# Patch switchTab to also update sidebar and title
old_switch = """  function switchTab(tab) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.sidebar-item[data-tab]').forEach(i => i.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    document.querySelector(`.sidebar-item[data-tab="${tab}"]`)?.classList.add('active');
    document.getElementById('page-title').textContent = { overview:'Overview', properties:'Properties', inquiries:'Inquiries', bookings:'Bookings', payments:'Payments', complaints:'Complaints', visitors:'Visitors' }[tab] || tab;
    const loaders = { properties: loadProperties, inquiries: loadInquiries, bookings: loadBookings, payments: loadPayments, complaints: loadComplaints, visitors: loadVisitors };
    if (loaders[tab]) loaders[tab]();
  }"""

new_switch = """  function switchTab(tab) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.sb-item[data-tab]').forEach(i => i.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    document.querySelector(`.sb-item[data-tab="${tab}"]`)?.classList.add('active');
    const titles = { overview:'Dashboard', properties:'Properties', inquiries:'Inquiries', bookings:'Bookings', payments:'Payments', complaints:'Complaints', visitors:'Visitors' };
    document.getElementById('page-title').textContent = titles[tab] || tab;
    closeSidebar();
    const loaders = { properties: loadProperties, inquiries: loadInquiries, bookings: loadBookings, payments: loadPayments, complaints: loadComplaints, visitors: loadVisitors };
    if (loaders[tab]) loaders[tab]();
  }

  function toggleSidebar() {
    document.getElementById('ds-sidebar').classList.toggle('open');
    document.getElementById('ds-overlay').classList.toggle('active');
  }
  function closeSidebar() {
    document.getElementById('ds-sidebar').classList.remove('open');
    document.getElementById('ds-overlay').classList.remove('active');
  }"""

if old_switch in html:
    html = html.replace(old_switch, new_switch)
    print('switchTab patched')
else:
    print('WARNING: switchTab not found, trying partial match')

# Add date to topbar
old_load = "  loadOverview();\n  loadNotifications();"
new_load = """  loadOverview();
  loadNotifications();
  // Topbar date
  document.getElementById('topbar-date').textContent =
    new Date().toLocaleDateString('en-IN', {weekday:'long',year:'numeric',month:'long',day:'numeric'});"""

if old_load in html:
    html = html.replace(old_load, new_load)
    print('date init patched')

# Patch loadOverview to also populate ring, bars, badges
old_overview_end = "    } catch (e) { Toast.error('Failed to load overview.'); }\n  }"
new_overview_end = """      // Update sidebar badges
      const pendingCount = bookings.filter(b => b.status === 'pending').length;
      const openCount    = tickets.filter(t => t.status === 'pending' || t.status === 'open' || t.status === 'in_progress').length;
      const overdue      = 0; // placeholder
      const pBadge = document.getElementById('sb-badge-bookings');
      const cBadge = document.getElementById('sb-badge-complaints');
      if (pendingCount > 0) { pBadge.textContent = pendingCount; pBadge.style.display = ''; }
      if (openCount > 0)    { cBadge.textContent = openCount;    cBadge.style.display = ''; }
      document.getElementById('attn-bookings').textContent   = pendingCount;
      document.getElementById('attn-complaints').textContent = openCount;
      document.getElementById('attn-payments').textContent   = overdue || '0';

      // Occupancy bars per property
      const barsEl = document.getElementById('occ-bars');
      if (props.length) {
        let totalBeds = 0, totalOcc = 0;
        barsEl.innerHTML = props.map(p => {
          const rooms = p.rooms || [];
          const total = rooms.reduce((s,r) => s + (r.total_beds||1), 0);
          const avail = rooms.reduce((s,r) => s + (r.available_beds||0), 0);
          const occ   = total - avail;
          totalBeds += total; totalOcc += occ;
          const pct   = total ? Math.round((occ / total) * 100) : 0;
          const color = pct >= 80 ? '#e05656' : pct >= 60 ? '#E59B22' : '#43A06A';
          return `<div>
            <div class="occ-bar-label"><span>${p.name}</span><span>${pct}% &middot; ${occ}/${total} beds</span></div>
            <div class="occ-bar-track"><div class="occ-bar-fill" style="background:${color}" data-w="${pct}%"></div></div>
          </div>`;
        }).join('');
        setTimeout(() => {
          document.querySelectorAll('.occ-bar-fill[data-w]').forEach(el => { el.style.width = el.dataset.w; });
        }, 200);
        // Ring
        const pct = totalBeds ? Math.round((totalOcc / totalBeds) * 100) : 0;
        document.getElementById('ringPct').textContent = pct + '%';
        document.getElementById('ring-occupied').textContent = totalOcc;
        document.getElementById('ring-available').textContent = totalBeds - totalOcc;
        const circ = 2 * Math.PI * 40;
        setTimeout(() => {
          const ring = document.getElementById('ringFill');
          if (ring) { ring.style.strokeDasharray = circ; ring.style.strokeDashoffset = circ - (pct/100)*circ; }
        }, 300);
      } else {
        barsEl.innerHTML = '<p style="color:#6B7B5A;font-size:.85rem;text-align:center;padding:12px;">No properties yet.</p>';
      }
    } catch (e) { Toast.error('Failed to load overview.'); }
  }"""

if old_overview_end in html:
    html = html.replace(old_overview_end, new_overview_end)
    print('loadOverview patched')
else:
    print('WARNING: loadOverview end not found')

f.write_text(html, encoding='utf-8')
print('Owner dashboard JS patched successfully')
