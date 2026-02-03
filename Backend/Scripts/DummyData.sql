INSERT INTO t_Agents (agentName, mobile, aadhar, email) VALUES
('Rohit Sharma', '9876543210', '123456789012', 'rohit@inventoryx.com'),
('Amit Verma',   '9876543211', '123456789013', 'amit@inventoryx.com'),
('Suresh Kumar', '9876543212', '123456789014', 'suresh@inventoryx.com'),
('Vikas Singh',  '9876543213', '123456789015', 'vikas@inventoryx.com'),
('Self',         '0000000000', NULL,             'self@inventoryx.com');



INSERT INTO t_Item
(name, description, qty, size, weight, manufactureYr, materialType, model, additionalParam1)
VALUES
('Scaffolding Pipe', 'Steel scaffolding pipe', 100, '10ft', '15kg', 2022, 'Steel', 'SP-10', 'Heavy Duty'),
('Wheel Barrow', 'Construction wheel barrow', 30, 'Standard', '25kg', 2021, 'Iron', 'WB-01', 'Rubber Wheel'),
('Concrete Mixer', 'Electric concrete mixer', 10, 'Large', '150kg', 2023, 'Steel', 'CM-500', 'Electric'),
('Ladder', 'Aluminium ladder', 40, '12ft', '12kg', 2022, 'Aluminium', 'LD-12', 'Foldable'),
('Drill Machine', 'Electric drill', 25, 'Medium', '5kg', 2023, 'Metal', 'DM-13', 'Corded'),
('Generator', 'Diesel generator', 8, 'Large', '200kg', 2020, 'Steel', 'DG-10', '5 KVA'),
('Water Pump', 'Industrial water pump', 15, 'Medium', '40kg', 2021, 'Iron', 'WP-02', 'Single Phase'),
('Road Roller', 'Mini road roller', 4, 'Large', '900kg', 2019, 'Steel', 'RR-1', 'Hydraulic'),
('Vibrator Machine', 'Concrete vibrator', 18, 'Small', '8kg', 2022, 'Steel', 'VM-20', 'High RPM'),
('Cutting Machine', 'Stone cutting machine', 12, 'Medium', '30kg', 2021, 'Steel', 'CM-9', 'Diamond Blade'),
('Safety Helmet', 'Construction helmet', 60, 'Universal', '1kg', 2023, 'Plastic', 'SH-1', 'ISI Mark'),
('Safety Belt', 'Worker safety belt', 45, 'Adjustable', '2kg', 2023, 'Nylon', 'SB-2', 'Double Lock'),
('Jack Hammer', 'Heavy jack hammer', 7, 'Large', '65kg', 2020, 'Steel', 'JH-3', 'Petrol'),
('Hand Trolley', 'Material trolley', 20, 'Medium', '35kg', 2022, 'Iron', 'HT-4', 'Solid Wheel'),
('Measuring Tape', 'Steel measuring tape', 80, '5m', '0.5kg', 2024, 'Steel', 'MT-5', 'Auto Lock');


INSERT INTO t_AvailableStock (itemId, qty, rentedOutQty) VALUES
(1,100,30),(2,30,10),(3,10,4),(4,40,15),(5,25,8),
(6,8,3),(7,15,5),(8,4,1),(9,18,6),(10,12,4),
(11,60,20),(12,45,12),(13,7,2),(14,20,6),(15,80,25);


INSERT INTO RentalPrice (itemId, itemName, rent, rentFrequency) VALUES
(1,'Scaffolding Pipe',50,'daily'),
(2,'Wheel Barrow',120,'daily'),
(3,'Concrete Mixer',1500,'daily'),
(4,'Ladder',80,'daily'),
(5,'Drill Machine',200,'daily'),
(6,'Generator',3000,'daily'),
(7,'Water Pump',600,'daily'),
(8,'Road Roller',8000,'daily'),
(9,'Vibrator Machine',250,'daily'),
(10,'Cutting Machine',400,'daily'),
(11,'Safety Helmet',20,'daily'),
(12,'Safety Belt',30,'daily'),
(13,'Jack Hammer',3500,'daily'),
(14,'Hand Trolley',150,'daily'),
(15,'Measuring Tape',10,'daily');


INSERT INTO t_party
(id, name, mobile, aadhaar, email, address, siteAddress, agentId, agentName, status)
VALUES
(UUID(),'ABC Constructions','9000000001','111122223333','abc@mail.com','Delhi','Noida Site',1,'Rohit Sharma','active'),
(UUID(),'Sharma Builders','9000000002','111122223334','sharma@mail.com','Gurgaon','Sector 56',2,'Amit Verma','active'),
(UUID(),'Kumar Infra','9000000003','111122223335','kumar@mail.com','Faridabad','NH-19',3,'Suresh Kumar','payment_due'),
(UUID(),'Verma Projects','9000000004','111122223336','verma@mail.com','Delhi','Dwarka',2,'Amit Verma','active'),
(UUID(),'Singh Contractors','9000000005','111122223337','singh@mail.com','Noida','Sector 62',4,'Vikas Singh','inactive');


INSERT INTO rentoutTxn
(partyId, contractId, partyName, agentId, agentName, itemId, itemQty)
SELECT id, 1001, name, agentId, agentName, 1, 10 FROM t_party LIMIT 1;

INSERT INTO rentoutTxn
(partyId, contractId, partyName, agentId, agentName, itemId, itemQty)
SELECT id, 1002, name, agentId, agentName, 3, 2 FROM t_party LIMIT 1 OFFSET 1;

INSERT INTO rentoutTxn
(partyId, contractId, partyName, agentId, agentName, itemId, itemQty)
SELECT id, 1003, name, agentId, agentName, 6, 1 FROM t_party LIMIT 1 OFFSET 2;


INSERT INTO returnTxn
(partyId, contractId, partyName, agentId, agentName, itemId, itemQty)
SELECT id, 1001, name, agentId, agentName, 1, 4 FROM t_party LIMIT 1;
