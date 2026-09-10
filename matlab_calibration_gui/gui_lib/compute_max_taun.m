function maxM = compute_max_taun(fn, alpha, gamma)
maxM = alpha*(abs(fn)^(gamma+1));
