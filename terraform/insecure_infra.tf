resource "aws_s3_bucket" "data" {
  bucket = "company-analytics-data"
}

resource "aws_s3_bucket_acl" "data_acl" {
  bucket = aws_s3_bucket.data.id
  acl    = "public-read"          
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_enc" {
  bucket = aws_s3_bucket.data.id
  # missing rule block entirely — no encryption configured
}

resource "aws_security_group" "app" {
  name = "app-sg"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   
  }
}

resource "aws_db_instance" "primary" {
  engine              = "postgres"
  instance_class      = "db.t3.medium"
  publicly_accessible = true       
  storage_encrypted   = false     
  skip_final_snapshot = true       
}

resource "aws_iam_role_policy" "admin_everything" {
  role   = aws_iam_role.app.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "*"                
      Resource = "*"
    }]
  })
}
