a, b = *ARGV

def true_positives(filename)
  `python compare_results.py #{filename} results.sample.tsv | tail -n +7` \
    .lines.map(&:strip).map { |line| line.split(' <-> ').map(&:to_i) }
end

tpa = true_positives(a)
tpb = true_positives(b)

print_comparison = lambda do |(x, y)|
  puts `ruby compare.rb #{x} #{y}`
end

puts "> in both results"
(tpb & tpa).each(&print_comparison)

puts "> in #{b} but not in #{a}"
(tpb - tpa).each(&print_comparison)

puts "> in #{a} but not in #{b}"
(tpa - tpb).each(&print_comparison)
