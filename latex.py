import datastore

def get_parse_point(content, parse_prefix):
    ''' Find all lines in content which starts with parse_prefix
        Return a list of all matchies 
    '''
    list = []
    for i in range(0, len(content)):
        if content[i][0:len(parse_prefix)] == parse_prefix:
            list.append(i)
    return list

def remove_trailing_space(string):
    ''' Return the string with trailing spaces removed '''
    non_space_pos = len(string)
    while (non_space_pos > 0) and (string[non_space_pos - 1] == ' '):
        non_space_pos -= 1
    return string[:non_space_pos]

def str_strip(content, prefix, suffix):
    ''' If content has the specified prefix and suffix, then return the stripped string
        Otherwise return empty string, the function will remove trailing spaces
    '''
    content = remove_trailing_space(content)
    if content[:len(prefix)] != prefix:
        return ''
    if content[-len(suffix):] != suffix:
        return ''
    return content[len(prefix):len(content) - len(suffix)]

def get_latex_content(root, level):
    ''' Generate Latex code for root node and all its descendents '''
    latex_content = ''
    children = datastore.get_child_of_entry(root.key)
    children.sort(key = lambda x:x.child_index)
    for entry in children:
        # Generating Begin Mark
        if entry.type == 'title':
            if level == 1:
                latex_content += '\subsection{' + entry.content + '}\n'
            elif level == 2:
                latex_content += '\subsubsection{' + entry.content + '}\n'
            elif level == 3:
                latex_content += '\paragraph{' + entry.content + '}\n'
            elif level == 4:
                latex_content += '\subparagraph{' + entry.content + '}\n'
        elif entry.type == 'equation':
            latex_content += entry.content + '\n\n'
        elif entry.type == 'paragraph':
            latex_content += entry.content + '\n\n'
        elif entry.type == 'ordered_list':
            latex_content += '\\begin{enumerate}\n'
        elif entry.type == 'list':
            latex_content += '\\begin{itemize}\n'
        elif entry.type == 'list_item':
            latex_content += '\item\n'
    
        # Recursively get child latex code
        latex_content += get_latex_content(entry, level + 1)

        # Generating End Mark
        if entry.type == 'ordered_list':
            latex_content += '\\end{enumerate}\n\n'
        elif entry.type == 'list':
            latex_content += '\\end{itemize}\n\n'

    # Return the latex code
    return latex_content

def is_valid_list(content):
    ''' Check whether the content is the latex code of a valid list '''
    begin = str_strip(content[0], '\\begin{', '}')
    end = str_strip(content[-1], '\\end{', '}')
    if begin != end or begin == '':
        return False
    for i in range(1, len(content) - 1):
        if content[i] != '':
            return (remove_trailing_space(content[i]) == '\\item')
    return True
 
def create_latex_node(content, root_key, child_index):
    ''' In this function we assume that whole content is from one single subtree '''
    # Determine the type of latex node
    type = 'paragraph'
    # If the first line contains equation indicator string, then set the type to be equation
    # Note that it may still be invalid equation, but since latex code of equation is not
    # modified, it is safe to have false positives
    equation_indicator = ['$$', '\\[', '\\begin{equation}', '\\begin{align}']
    for indicator in equation_indicator:
        if indicator in content[0]:
                type = 'equation'
    # If the content is a list:
    if is_valid_list(content):
        if str_strip(content[0], '\\begin{', '}') == 'enumerate':
            type = 'ordered_list'
        if str_strip(content[0], '\\begin{', '}') == 'itemize':
            type = 'list'

    # Create entry based on detected type
    entry_list = []
    if type == 'equation':
        new_key = root_key + ' eq' + str(child_index)
        entry = datastore.Entry(new_key, root_key, '\n'.join(content), 'equation', child_index)
        entry_list.append(entry)
    elif type == 'paragraph':
        new_key = root_key + ' p' + str(child_index)
        entry = datastore.Entry(new_key, root_key, '\n'.join(content), 'paragraph', child_index)
        entry_list.append(entry)
    elif type == 'ordered_list' or type == 'list':
        if type == 'ordered_list':
            new_key = root_key + ' ol' + str(child_index)
            entry = datastore.Entry(new_key, root_key, '', 'ordered_list', child_index)
        else:
            new_key = root_key + ' ul' + str(child_index)
            entry = datastore.Entry(new_key, root_key, '', 'list', child_index)
        entry_list.append(entry)
        # Now we track the items of this list
        last_item = -1
        item_index = 1
        for i in range(1, len(content)):
            if remove_trailing_space(content[i]) == '\\item' or i == len(content) - 1:
                if last_item != -1:
                    new_key = entry.key + ' li' + str(item_index)
                    item_entry = datastore.Entry(new_key, entry.key, '',
                                        'list_item', item_index)
                    item_index += 1
                    entry_list.append(item_entry)
                    entry_list += parse_latex_content(content[last_item + 1:i], new_key)
                last_item = i
    return entry_list

def parse_latex_content(content, root_key):
    ''' Parse the input content. 
        Return a list of content nodes with root at root_key. 
        The generated content node will guarantee to have equivalent latex code but
        probably with slightly different formatting.
        Note in this function we do not raise exception. Unlike conventional
        latex compiling, whenever we encounter uninterpretable content, we will
        treat them as plain string.
    '''
    if len(content) == 0:
        return []
    # If there are section partition points, parse the contents based on them
    prefix_list = ['\\section{', '\\subsection{', '\\subsubsection{', 
                   '\\paragraph{', '\\subparagraph{']
    for prefix in prefix_list:
        sec_list = get_parse_point(content, prefix)
        section_entry_list = []
        # Remove all illegal section partition points in sec_list
        for pos in sec_list:
            title = str_strip(content[pos], prefix, '}')
            if title == '':
                sec_list.remove(pos)

        # If we found partition points at this level
        if len(sec_list) > 0:        
            # First we construct all section partitions' range
            sec_begin = [0] + sec_list
            sec_end = sec_list + [len(content)]
            
            # Parse all the partitions
            entry_list = []
            # First partition is special because it does not belong to
            # any subsection
            section_content = content[sec_begin[0]:sec_end[0]]
            entry_list += parse_latex_content(section_content, root_key)
            # Calculate child_index starting point, it counts the number
            # of entries in entry_list with parent equals root_key, and then plus 1
            next_child_index = len(filter(lambda x:x.parent_key == root_key, entry_list)) + 1
            # Parse subsection children
            for i in range(1, len(sec_begin)):
                # Create title node
                title = str_strip(content[sec_begin[i]], prefix, '}') 
                sec_entry = datastore.Entry(root_key + '.' + str(i), root_key, 
                                            title, 'title', next_child_index)
                entry_list.append(sec_entry)
                next_child_index += 1
                # Parse section content
                section_content = content[sec_begin[i] + 1:sec_end[i]]
                entry_list += parse_latex_content(section_content, sec_entry.key)
            return entry_list
            
    # Otherwise, parse the contents based on empty lines
    # First label all matching \begin, \end pairs
    counter = [0 for _ in range(0, len(content))]
    begin_lines = []
    for i in range(0, len(content)):
        in_begin = str_strip(content[i], '\\begin{', '}')
        if in_begin == 'enumerate' or in_begin == 'itemize':
            begin_lines.append((i, in_begin))
        in_end = str_strip(content[i], '\\end{', '}')
        if (in_end == 'enumerate' or in_end == 'itemize') and (len(begin_lines) > 0):
            last_begin = begin_lines.pop()
            if is_valid_list(content[last_begin[0]:i + 1]):
                counter[last_begin[0]] = 1
                counter[i] = -1
        
    # Determine the ranges of every partition    
    sec_begin = []
    sec_end = []
    last_partition_end = -1
    counter_sum = 0
    counter_stack = []
    for i in range(0, len(content)):
        if counter[i] == 1:
            counter_stack.append(i)
            counter_sum += 1
        if counter[i] == -1:
            counter_sum -= 1
            if counter_sum == 0:
                # There might be another paragraph just before '\begin'
                sec_begin.append(last_partition_end + 1)
                sec_end.append(counter_stack[0] - 1)
                # The range of the list
                sec_begin.append(counter_stack[0])
                sec_end.append(i)
                last_partition_end = i
            counter_stack.pop()
        if content[i] == '' and counter_sum == 0:
            sec_begin.append(last_partition_end + 1)
            sec_end.append(i - 1)
            last_partition_end = i
    # We need to add the last partition manually sometimes
    sec_begin.append(last_partition_end + 1)
    sec_end.append(len(content) - 1)        
    
    # Parse all partitions
    entry_list = []
    child_index = 1
    for i in range(0, len(sec_begin)):
        # Both ends are inclusive
        section_content = content[sec_begin[i]:sec_end[i] + 1]
        if len(section_content) > 0:
            new_node = create_latex_node(section_content, root_key, child_index)
            child_index += 1
            entry_list += new_node
    return entry_list

