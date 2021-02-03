### When using the inverse `-v` option:
`Xpercent_of_b` = `bedtools intersect -F X`
This means that any overlap between `a` and `b` that is smaller than X fraction of `b` will be included in the inverse output (i.e. included as a 'non-overlaping' region).<br>
This is usefull to signify for example areas where there might be a small overlap but most of `b` is non overlapping.<br>
example:
 *see the README file on local machine*

In this case it might  be a good option to (also?) report the feature in `b`
