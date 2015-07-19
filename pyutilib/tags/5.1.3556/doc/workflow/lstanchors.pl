#!/usr/bin/env perl

$re = '^(.*?)(\\listing|\\autobreaklisting|\\scriptsizelisting|\\tinylisting)\{([^\}]*)\}\{([^\}]*)\}(\{[^\}]*\}\{[^\}]*\})?(.*)';

unless ( @ARGV )
  { die "Usage: $0 target.tex ...\n"; }

foreach $f ( @ARGV )
  {
  unless ( -f $f and -r $f and -w $f )
    {
    print "File '$f' does not appear to be a valid target.  Skipping.\n";
    next;
    }
  print "Updating $f\n";
  &update_file($f);
  }

exit 0;


sub update_file($)
  {
  my($fname) = @_;

  open FILE, "<$fname" or die "Error opening TeX file $fname\n";

  my(@lines) = ();
  foreach $line ( <FILE> )
    {
    unless ( $line =~ /$re/so )
      { push @lines, $line; }
    else
      {
      print "Updating reference: $line";
      my($front) = $1;
      my($cmd)   = $2;
      my($file)  = $3;
      my($anchor)= $4;
      my($firstlast) = $5;
      my($end)   = $6;

      my($firstline) = -1;
      my($lastline) = -1;
      open REF, "<$file" or die("Error opening referenced file $file ".
                                "while processing $fname\n");
      my($lineno) = 0;
      # scan file for the anchor tags (start = '@anchor:', end = '@:anchor')
      while ( $_ = <REF> )
        {
        ++$lineno;
        if ( /\@${anchor}:/ )
          {
          if ( $firstline != -1 )
            { die("Error: multiple starting tags found for anchor $anchor ".
                  " in file $file while processing $fname"); }
          $firstline = $lineno+1;
          }
        if ( /\@:${anchor}$/ )
          {
          if ( $lastline != -1 )
            { die("Error: multiple ending tags found for anchor $anchor ".
                  " in file $file while processing $fname"); }
          $lastline = $lineno-1;
          }
        }
      close REF;

      if ( $firstline == -1 )
        { $firstline = 1; }
    
      if ( $lastline == -1 )
        { $lastline = $lineno-1; }
      
      # form the modified line
      chomp($end);
      if ($anchor eq '') 
         { 
         my($tmp) = $lineno - 1;
         push @lines, "${front}${cmd}{$file}{$anchor}{1}{$lineno}$end\n";
         }
      else
         { push @lines, "${front}${cmd}{$file}{$anchor}{$firstline}{$lastline}$end\n"; }
      }
    }

  close FILE;
  open FILE, ">$fname" or die "Error overwriting file $fname\n";
  print FILE join '', @lines;
  close FILE;
  }
