(1..3).each do |i|
	Process.fork do
		threshold = 0.4 + 0.05 * i
		`env PATH=/usr/local/bin:$PATH python detect_duplicates.py -s dice -m arithemtic_weighted_mean addresses.tsv #{threshold} results/#{threshold}.tsv`
	end
end
