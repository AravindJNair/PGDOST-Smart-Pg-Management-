from django.http import HttpResponse

def api_docs(request):
    html = """
    <html>
        <head>
            <title>PGDOST API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #2e7d32; }
                h2 { color: #1b5e20; border-bottom: 1px solid #ccc; padding-bottom: 5px; }
                ul { list-style-type: none; padding: 0; }
                li { margin-bottom: 10px; background: #f1f8e9; padding: 10px; border-radius: 5px; }
                .method { font-weight: bold; padding: 3px 8px; border-radius: 3px; margin-right: 10px; color: white;}
                .get { background-color: #4CAF50; }
                .post { background-color: #2196F3; }
                .patch { background-color: #FF9800; }
                .delete { background-color: #f44336; }
                code { background: #eee; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>PGDOST API Documentation</h1>
            <p>Welcome to the basic API documentation for the PGDOST project.</p>

            <h2>Authentication (Accounts)</h2>
            <ul>
                <li><span class="method post">POST</span> <code>/api/auth/register/</code> - Register a new user</li>
                <li><span class="method post">POST</span> <code>/api/auth/login/</code> - Login to get JWT access and refresh tokens</li>
                <li><span class="method post">POST</span> <code>/api/auth/token/refresh/</code> - Refresh an access token</li>
                <li><span class="method get">GET</span> <code>/api/auth/profile/</code> - Get logged-in user profile</li>
                <li><span class="method get">GET</span> <code>/api/auth/notifications/</code> - Get notifications</li>
                <li><span class="method patch">PATCH</span> <code>/api/auth/notifications/&lt;id&gt;/</code> - Mark notification as read</li>
            </ul>

            <h2>Properties (Marketplace & Owner)</h2>
            <ul>
                <li><span class="method get">GET</span> <code>/api/properties/</code> - List public approved properties</li>
                <li><span class="method get">GET</span> <code>/api/properties/&lt;id&gt;/</code> - Get public property details</li>
                <li><span class="method get">GET</span> <span class="method post">POST</span> <code>/api/properties/&lt;property_pk&gt;/reviews/</code> - List or create property reviews</li>
                <li><span class="method post">POST</span> <code>/api/properties/&lt;property_pk&gt;/inquire/</code> - Submit an inquiry for a property</li>
                <li><span class="method get">GET</span> <span class="method post">POST</span> <code>/api/properties/owner/</code> - List or create owner properties</li>
                <li><span class="method get">GET</span> <span class="method post">POST</span> <code>/api/properties/owner/&lt;property_pk&gt;/rooms/</code> - Manage rooms</li>
                <li><span class="method get">GET</span> <code>/api/properties/owner/inquiries/</code> - View received inquiries</li>
                <li><span class="method get">GET</span> <span class="method post">POST</span> <code>/api/properties/owner/&lt;property_pk&gt;/images/</code> - Upload or list property images</li>
                <li><span class="method patch">PATCH</span> <span class="method delete">DELETE</span> <code>/api/properties/owner/&lt;property_pk&gt;/images/&lt;image_pk&gt;/</code> - Update or delete property images</li>
            </ul>

            <h2>Bookings</h2>
            <ul>
                <li><span class="method post">POST</span> <code>/api/bookings/apply/</code> - Apply for a PG (Resident)</li>
                <li><span class="method get">GET</span> <code>/api/bookings/my/</code> - View own bookings (Resident)</li>
                <li><span class="method get">GET</span> <code>/api/bookings/active/</code> - View current active booking (Resident)</li>
                <li><span class="method get">GET</span> <code>/api/bookings/owner/</code> - View bookings for owned properties (Owner)</li>
                <li><span class="method patch">PATCH</span> <code>/api/bookings/owner/&lt;id&gt;/update/</code> - Update booking status (Owner)</li>
                <li><span class="method get">GET</span> <code>/api/bookings/all/</code> - View all bookings (Admin)</li>
            </ul>

            <h2>Complaints</h2>
            <ul>
                <li><span class="method get">GET</span> <span class="method post">POST</span> <code>/api/complaints/my/</code> - List or create complaints (Resident)</li>
                <li><span class="method get">GET</span> <code>/api/complaints/owner/</code> - View complaints for properties (Owner)</li>
                <li><span class="method get">GET</span> <code>/api/complaints/&lt;ticket_pk&gt;/replies/</code> - Add a reply to a complaint ticket</li>
                <li><span class="method patch">PATCH</span> <code>/api/complaints/owner/&lt;id&gt;/status/</code> - Update complaint status/reply (Owner)</li>
                <li><span class="method get">GET</span> <code>/api/complaints/all/</code> - View all complaints (Admin)</li>
            </ul>

            <h2>Payments</h2>
            <ul>
                <li><span class="method get">GET</span> <code>/api/payments/my/</code> - View own invoices (Resident)</li>
                <li><span class="method patch">PATCH</span> <code>/api/payments/my/&lt;id&gt;/pay/</code> - Mark invoice as paid</li>
                <li><span class="method post">POST</span> <code>/api/payments/owner/create/</code> - Create an invoice (Owner)</li>
                <li><span class="method get">GET</span> <code>/api/payments/owner/</code> - View owner invoices</li>
                <li><span class="method get">GET</span> <code>/api/payments/owner/&lt;id&gt;/</code> - View a single owner invoice</li>
                <li><span class="method get">GET</span> <code>/api/payments/all/</code> - View all invoices (Admin)</li>
            </ul>
        </body>
    </html>
    """
    return HttpResponse(html)
