BILLBOARD_STATUS = (
    ('Good', 'Good'),
    ('Broken', 'Broken'),
    ('Under Maintenance', 'Under Maintenance'),
    ('Not Working', 'Not Working'),
    ('Not Clear', 'Not Clear'),
    ('Not Visible', 'Not Visible'),
    ('Other', 'Other'),
)
BILLBORD_CATEGORY = [
    ('Category 1', 'Category 1'),
    ('Category 2', 'Category 2'),
    ('Category 3', 'Category 3'),
    ('Category 4', 'Category 4'),
    ('Category 5', 'Category 5'),
]

BILLBORD_TYPES = (
    ('LED', 'LED'),
    ('Digital', 'Digital'),
    ('Static', 'Static'),
)

MONITOR_TIME = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
     ('3', '4'),
) 

TASK_CHOICES = (
    ('ACCEPTED','ACCEPTED'),
    ('REJECTED','REJECTED'),
    ('PENDING','PENDING'),
    ('COMPLETED','COMPLETED'),
    
    
)
BILLBORD_FACES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
)

CAMPAIGN_TYPE = (
    ('Analytics', 'Analytics'),
    ('Monitoring', 'Monitoring'),
    ('Basic', 'Basic'),
)

APPROVAL_STATUS = (
    ('PENDING', 'PENDING'),
    ('APPROVED', 'APPROVED'),
    ('REJECTED', 'REJECTED'),
)


LOCATION_TYPE = (
    ('City', 'City'),
    ('Rural', 'Rural'),
    ('Suburban', 'Suburban'),
    ('Other', 'Other'),
)

TRAFFIC_DIRECTION = (
    ('Inbound', 'Inbound'),
    ('Outbound', 'Outbound'),
    ('Both', 'Both'),
)

STRUCTURE_TYPE = (
    ('Billboard', 'Billboard'),
    ('Pole', 'Pole'),
    ('Other', 'Other'),
)

POI_TYPE = (
    ('Restaurant', 'Restaurant'),
    ('Hotel', 'Hotel'),
    ('School', 'School'),
    ('Hospital', 'Hospital'),
    ('Bank', 'Bank'),
    ('ATM', 'ATM'),
    ('Bus Stop', 'Bus Stop'),
    ('Train Station', 'Train Station'),
    ('Airport', 'Airport'),
    ('Other', 'Other'),
)

BC_CATEGORY = (
    ('Food Store', 'Food Store'),
    ('Entertainment', 'Entertainment'),
    ('Retail', 'Retail'),
    ('Service', 'Service'),
    ('Office', 'Office'),
    
    ('Other', 'Other'),
)


POI_STATUS = (
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
    ('Other', 'Other'),
)

OBJECT_TYPE =(
    ('Person', 'Person'),
    ('Car', 'Car'),
    ('Bus', 'Bus'),
    ('Motorcycle', 'Motorcycle'),
    ('Truck', 'Truck'),
    ('Van', 'Van'),
    ('Animal', 'Animal'),
    ('Other', 'Other'),
)

WEEK_DAY = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
)

STATUS = (
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
)