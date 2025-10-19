-- Fix MySQL User Permissions for Mechanic Shop V4 Database
-- Run this if you encounter permission errors

-- Grant all privileges to root user for the database
GRANT ALL PRIVILEGES ON mechanic_shop_v4.* TO 'root'@'localhost';

-- If you're using a different user, replace 'root' and 'localhost' with your username and host
-- Example for user 'mechanic_user' from any host:
-- GRANT ALL PRIVILEGES ON mechanic_shop_v4.* TO 'mechanic_user'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Verify privileges (optional)
SHOW GRANTS FOR 'root'@'localhost';

SELECT 'User permissions updated successfully!' AS message;
