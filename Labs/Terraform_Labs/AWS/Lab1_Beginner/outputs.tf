output "ec2_instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.myec2.id
}

output "ec2_subnet_id" {
  description = "Subnet the EC2 is actually running in"
  value       = aws_instance.myec2.subnet_id
}

output "my_subnet_id" {
  description = "ID of the subnet we created"
  value       = aws_subnet.mysubnet1.id
}

output "ami_used" {
  description = "Ubuntu image Terraform looked up"
  value       = data.aws_ami.ubuntu.id
}

output "model_bucket_name" {
  description = "Name of the S3 bucket for model files"
  value       = aws_s3_bucket.models.bucket
}