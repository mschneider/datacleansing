(1..6).each do |i|
	Process.fork do
		threshold = 0.5 + 0.05 * i
		`env PATH=/usr/local/bin:$PATH python detect_duplicates.py -s damreau_levenshtein -m arithemtic_weighted_mean addresses.tsv #{threshold} results/#{threshold}.tsv`
	end
end
