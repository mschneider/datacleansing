(1..8).each do |i|
	Process.fork do
		`env PATH=/usr/local/bin:$PATH python detect_duplicates.py addresses.tsv #{i} results/#{i}.tsv`
	end
end
