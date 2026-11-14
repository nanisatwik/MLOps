variable "aws_region" {
  description = "AWS region where everything is created"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "Size of the EC2 machine"
  type        = string
  default     = "t2.micro"
}