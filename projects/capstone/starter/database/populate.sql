INSERT INTO carrier (name, active) VALUES ('Stephan Express', TRUE), ('Purolator', TRUE), ('UPS', TRUE);

INSERT INTO packager (first_name, last_name, initials, active) VALUES ('John', 'Doe', 'JD', TRUE), ('Mary', 'Smith', 'MS', TRUE), ('Fred', 'Fox', 'FF', TRUE);

INSERT INTO shipment (reference, carrier_id, packages, weight, tracking, packaged_by, create_date) 
VALUES
(45322, 4, 3, 30, 'XF430000095', 1, '2020-11-14 9:35AM')
,(45323, 4, 2, 30, 'XF430000099', 1, '2020-11-14 10:35AM')
,(45350, 5, 4, 30, '1234565655443333', 1, '2020-11-14 2:20PM')
,(45355, 5, 1, 7, '1234565655453300', 1, '2020-11-14 2:35PM')
,(45371, 6, 2, 5.8, 'AWX120000000K100', 1, '2020-11-15 9:35AM')
,(45377, 6, 3, 18.9, 'AWX120000000K100', 1, '2020-11-15 9:50AM')
,(45380, 6, 3, 30, 'AWX120000000K100', 1, '2020-11-15 10:35AM')
,(45388, 4, 5, 40, 'XF430000200', 1, '2020-11-15 10:45AM')
,(45390, 5, 7, 49, '1234565655443444', 1, '2020-11-15 1:15PM');


-- select count(id) as total_shipments, sum(packages) as total_pkg, sum(weight) as total_weight, date(create_date) as created from shipment group by created;

