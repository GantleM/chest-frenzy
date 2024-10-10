def sizeof_number(number, currency=None):
    """
    format values per thousands : K-thousands, M-millions, B-billions. 
    
    parameters:
    -----------
    number is the number you want to format
    currency is the prefix that is displayed if provided (€, $, £...)
    
    """
    currency='' if currency is None else currency

    if number < 1000:
        return f"{currency}{number}"

    #     #60 sufixes
    sufixes = [ "", "K", "M", "B", "T", "qa", "qu", "s", "oc", "no", 
                "d", "ud", "dd", "td", "qt", "qi", "se", "od", "nd","v", 
                "uv", "dv", "tv", "qv", "qx", "sx", "ox", "nx", "tn", "Qa",
                "Qu", "S", "Oc", "No", "D", "Ud", "Dd", "Td", "Qt", "Qi",
                "Se", "Od", "Nd", "V", "Uv", "Dv", "Tv", "Qv", "Qx", "Sx",
                "Ox", "Nx", "Tn", "x", "xx", "xxx", "X", "XX", "XXX", "END"] 
    for unit in sufixes:

        if abs(number) < 1000.0:
            return f"{currency}{number:.2f}{unit}"
        
        number /= 1000.0
    return f"{currency}{number:,}"


