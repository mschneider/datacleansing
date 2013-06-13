def lookup_address(id)
  line = id+1
  `tail -n +#{line} addresses.tsv | head -n 1`
end

a, b = *ARGV[1..2].map(&:to_i)
puts lookup_address(a)
puts lookup_address(b)
