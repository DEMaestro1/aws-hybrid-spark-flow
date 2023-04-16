terraform {
	required_providers {
		aws = {
			source = "hashicorp/aws"
			version = "~> 4.0"
		}
	}
}

variable rds_user {
	type = string
}

variable rds_pass {
	type = string
}

variable db_name {
	type = string
}

variable s3_bucker_name{
  type = string
}

#configure the provider
provider "aws" {
  region = "eu-north-1"
}


resource "aws_s3_bucket" "bucket_1" {
  bucket = var.s3_bucker_name
  tags = {
	Name = "For Project"
  }
}

resource "aws_db_instance" "proj-test" {
  allocated_storage = 20
  storage_type = "gp2"
  identifier = var.db_name
  db_name = var.db_name 
  engine = "postgres"
  engine_version = "14.6"
  instance_class = "db.t3.micro"
  username = var.rds_user
  password = var.rds_pass
  publicly_accessible = true
  skip_final_snapshot = true
  tags = {
	Name = "For Project"
  }
 }