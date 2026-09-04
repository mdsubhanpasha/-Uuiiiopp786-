# Route53 Hosted Zone Data Source
data "aws_route53_zone" "primary" {
  name         = var.domain_name
  private_zone = false
}

# Route53 Apex A Record -> Elastic IP
resource "aws_route53_record" "apex_a" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = var.domain_name
  type    = "A"
  ttl     = 300
  records = [aws_eip.edge_eip.public_ip]
}

# Route53 www CNAME Record -> Apex Domain
resource "aws_route53_record" "www_cname" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = "www.${var.domain_name}"
  type    = "CNAME"
  ttl     = 300
  records = [var.domain_name]
}
