terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
} 

provider "aws" {
  region = var.aws_region # CHANGED: now comes from variables.tf
}

# resource "<provider>_<resource_type>" "<resource_name>" {
#     <attribute> = "<value>"
# }

# NEW: look up the latest official Ubuntu 24.04 image instead of hardcoding an AMI ID
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical, the company that publishes Ubuntu

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

resource "aws_instance" "myec2" {
  ami           = data.aws_ami.ubuntu.id  # CHANGED: use the looked-up image
  instance_type = var.instance_type        # CHANGED: now comes from variables.tf
  subnet_id     = aws_subnet.mysubnet1.id  # NEW: put EC2 inside our own subnet
  tags = {
    Name = "myec2"
  }
}

resource "aws_subnet" "mysubnet1" {
  vpc_id     = aws_vpc.myvpc.id
  cidr_block = "10.0.1.0/24"
  tags = {
    Name = "mysubnet1"
  }
}

resource "aws_vpc" "myvpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "myvpc"
  }
}

# NEW: S3 bucket to store trained model files
resource "aws_s3_bucket" "models" {
  bucket_prefix = "satwik-mlops-models-" # AWS adds a unique ending to this
  force_destroy = true                   # lets terraform destroy delete it even if files are inside

  tags = {
    Name = "model-artifacts"
  }
}

# NEW: keep old versions of every file uploaded to the bucket
resource "aws_s3_bucket_versioning" "models" {
  bucket = aws_s3_bucket.models.id

  versioning_configuration {
    status = "Enabled"
  }
}