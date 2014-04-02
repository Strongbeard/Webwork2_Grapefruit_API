#!/usr/bin/env perl

# Webwork password encryption function.
# Used by AddUser.py to add encrypted passwords to webwork's password table.

print cryptPassword($ARGV[0]);

sub cryptPassword($) {
	my ($clearPassword) = @_;
	my $salt = join("", ('.','/','0'..'9','A'..'Z','a'..'z')[rand 64, rand 64]);
	my $cryptPassword = crypt($clearPassword, $salt);
	return $cryptPassword;
}
