# MongoDB Atlas Connection Troubleshooting Guide

## Current Issue
**Authentication Failed**: The connection string `mongodb+srv://2024081204:anushka@cluster0.fn8yhfs.mongodb.net/` is failing with authentication error.

## Step-by-Step Troubleshooting

### 1. Verify MongoDB Atlas Cluster Status
- Log into [MongoDB Atlas](https://cloud.mongodb.com/)
- Check if your cluster `Cluster0` is running (green status)
- Ensure the cluster is not paused or suspended

### 2. Check Database User
- In MongoDB Atlas, go to **Database Access**
- Verify user `2024081204` exists
- Check the password is `anushka`
- Ensure the user has proper roles:
  - `readWrite` on database `it`
  - OR `readWriteAnyDatabase` for full access

### 3. Verify IP Whitelist
- In MongoDB Atlas, go to **Network Access**
- Add your current IP address OR
- **For testing**: Add `0.0.0.0/0` (allows all IPs - remove after testing)

### 4. Test Connection String Format
Your connection string should be:
```
mongodb+srv://2024081204:anushka@cluster0.fn8yhfs.mongodb.net/it?retryWrites=true&w=majority&appName=Cluster0
```

### 5. Alternative Connection Strings to Try

#### Option A: Without database name
```
mongodb+srv://2024081204:anushka@cluster0.fn8yhfs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

#### Option B: With URL-encoded password (if special characters)
```
mongodb+srv://2024081204:anushka@cluster0.fn8yhfs.mongodb.net/it?retryWrites=true&w=majority&appName=Cluster0
```

#### Option C: Standard MongoDB connection (if SRV fails)
```
mongodb://2024081204:anushka@cluster0-shard-00-00.fn8yhfs.mongodb.net:27017,cluster0-shard-00-01.fn8yhfs.mongodb.net:27017,cluster0-shard-00-02.fn8yhfs.mongodb.net:27017/it?ssl=true&replicaSet=atlas-xxxxx-shard-0&authSource=admin&retryWrites=true&w=majority
```

### 6. Test with MongoDB Compass
1. Download [MongoDB Compass](https://www.mongodb.com/products/compass)
2. Use the connection string to connect
3. If Compass works, the issue is in our Python code
4. If Compass fails, the issue is with Atlas configuration

### 7. Create New Database User (if needed)
If the user doesn't exist:
1. Go to **Database Access** in MongoDB Atlas
2. Click **Add New Database User**
3. Choose **Password** authentication
4. Username: `2024081204`
5. Password: `anushka`
6. Database User Privileges: `readWriteAnyDatabase`
7. Click **Add User**

### 8. Check Cluster Configuration
- Ensure cluster is M0 (free tier) or higher
- Check if cluster has any restrictions
- Verify the cluster region is accessible

## Next Steps

1. **First**: Check IP whitelist (add 0.0.0.0/0 for testing)
2. **Second**: Verify user exists with correct password
3. **Third**: Test with MongoDB Compass
4. **Fourth**: Try the alternative connection strings above

## Quick Fix Commands

After fixing Atlas configuration, test with:

```bash
# Test the connection
python scripts/test_direct_connection.py

# If successful, add sample data
python scripts/add_test_data.py

# View the data
python scripts/view_database.py
```

## Contact Information
If you continue having issues:
1. Share a screenshot of your MongoDB Atlas Database Access page
2. Share a screenshot of your Network Access page
3. Confirm the exact cluster name and region
