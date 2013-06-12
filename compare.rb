def lookup_address(id)
  line = id+1
  `head -n #{line} addresses.tsv | tail -n 1`
end

a, b = *ARGV.map(&:to_i)
puts lookup_address(a)
puts lookup_address(b)
