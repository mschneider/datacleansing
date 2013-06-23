
puts %w[filename false-positives false-negatives true-positives precision recall f-measure].join(',')
Dir.glob("results/*.tsv").each do |filename|
  result = Hash[`python compare_results.py #{filename} results.sample.tsv | tail -n +3 | awk 'NR < 7 {print $0}'`.lines.map(&:strip).map { |line| line.split(': ') }]
  puts ([filename] + result.values).join(',')
end
