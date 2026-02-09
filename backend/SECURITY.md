# MongoDB Security Guide for Production

## 1. Database-Level Security

### Authentication
```bash
# Create admin user in MongoDB
mongo admin
db.createUser({
  user: "admin",
  pwd: "strong-password-here",
  roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase", "readWriteAnyDatabase"]
})

# Create application-specific user
mongo napling_choice_awards
db.createUser({
  user: "napling_app",
  pwd: "app-specific-password",
  roles: ["readWrite"]
})
```

### Network Security
- **Enable SSL/TLS**: Use `ssl=true` in connection string
- **Whitelist IP addresses**: Restrict database access to application servers only
- **Use VPC/Private Networks**: Keep database traffic off public internet

### MongoDB Configuration
```javascript
// /etc/mongod.conf
net:
  port: 27017
  bindIp: 127.0.0.1,10.0.0.1  # Specific IPs only

security:
  authorization: enabled
  javascriptEnabled: false
```

## 2. Application-Level Security

### Environment Variables
```bash
# Production .env file
MONGODB_URI=mongodb://napling_app:password@mongodb-host:27017/napling_choice_awards
MONGODB_SSL=true
MONGODB_AUTH_SOURCE=napling_choice_awards
SECRET_KEY=your-very-secure-secret-key-here
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
RATE_LIMIT_PER_MINUTE=60
```

### Connection Security Features
- **SSL/TLS encryption** for all database connections
- **Connection timeouts** to prevent hanging
- **Authentication source** specification
- **Input validation** and sanitization
- **Rate limiting** per endpoint

## 3. Deployment Security

### Docker Security
```dockerfile
# Use non-root user
USER appuser
# Minimal base image
FROM python:3.12-slim
# Health checks
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD curl -f http://localhost:5000/health || exit 1
```

### Firewall Rules
```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw deny 27017/tcp  # Block MongoDB from external access
```

## 4. Monitoring & Logging

### Security Monitoring
- **Failed authentication attempts**
- **Unusual query patterns**
- **Rate limit violations**
- **IP-based anomaly detection**

### Audit Logging
```python
# Add to your application
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log security events
logger.warning(f"Rate limit exceeded for IP: {request.remote_addr}")
logger.info(f"User action: {action} from IP: {request.remote_addr}")
```

## 5. Backup Security

### Encrypted Backups
```bash
# Create encrypted backup
mongodump --uri="mongodb://user:pass@host:27017/db" --gzip --archive=backup.gz
gpg --symmetric --cipher-algo AES256 backup.gz
```

### Access Control
- **Separate backup credentials**
- **Role-based access** to backup files
- **Regular backup testing**
- **Off-site storage**

## 6. Security Checklist

### Pre-Deployment
- [ ] Enable authentication in MongoDB
- [ ] Configure SSL/TLS
- [ ] Set up firewall rules
- [ ] Create application-specific database user
- [ ] Configure environment variables
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Test backup/restore procedures

### Ongoing
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Review user permissions
- [ ] Test disaster recovery
- [ ] Security audit quarterly

## 7. Common Vulnerabilities & Mitigations

### SQL/NoSQL Injection
- **Input validation** implemented
- **Parameterized queries** via PyMongo
- **Object ID validation** for all ID parameters

### Rate Limiting
- **Global rate limit**: 60 requests/minute
- **Upload endpoint**: 10 requests/minute  
- **Voting endpoint**: 5 requests/minute
- **Content creation**: 20 requests/minute

### File Upload Security
- **File type restrictions** (images only)
- **File size limits** (16MB max)
- **Secure filename handling**
- **Upload directory protection**

### CORS Configuration
- **Specific allowed origins**
- **Explicit HTTP methods**
- **No wildcard origins** in production
