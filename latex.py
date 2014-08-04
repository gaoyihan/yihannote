import datastore

def get_parse_point(content, parse_prefix):
    list = []
    for i in range(0, len(content)):
        if content[i][0:len(parse_prefix)] == parse_prefix:
            list.append(i)
    return list

def str_strip(content, prefix, end_mark):
    end_index = content.index(end_mark)
    return content[len(prefix):end_index]

def get_latex_content(entry, level):
    ''' This function actually get the latex content of all descendents of the entry '''
    latex_content = ''
    children = datastore.get_child_of_entry(entry.key)
    children.sort(key = lambda x:x.child_index)
    for entry in children:
        if (entry.type == 'title'):
            if level == 1:
                latex_content += '\subsection{' + entry.content + '}\n'
            elif level == 2:
                latex_content += '\subsubsection{' + entry.content + '}\n'
            elif level == 3:
                latex_content += '\paragraph{' + entry.content + '}\n'
            elif level == 4:
                latex_content += '\subparagraph{' + entry.content + '}\n'
        elif (entry.type == 'equation'):
            latex_content += entry.content + '\n\n'
        elif (entry.type == 'paragraph'):
            latex_content += entry.content + '\n\n'
        elif (entry.type == 'ordered_list'):
            latex_content += '\\begin{enumerate}\n'
        elif (entry.type == 'list'):
            latex_content += '\\begin{itemize}\n'
        elif (entry.type == 'list_item'):
            latex_content += '\item\n'
        latex_content += get_latex_content(entry, level + 1)
        if (entry.type == 'ordered_list'):
            latex_content += '\\end{enumerate}\n\n'
        elif (entry.type == 'list'):
            latex_content += '\\end{itemize}\n\n'
    return latex_content

def create_latex_node(content, root_key, child_index):
    if len(content) == 0:
        return []
    # Determine the type of latex node
    type = 'paragraph'
    equation_indicator = ['$$', '\\[', '\\begin{equation', '\\begin{align']
    for line in content:
        for indicator in equation_indicator:
            if indicator in line:
                type = 'equation'
    if '\\begin{enumerate}' in content[0]:
        type = 'ordered_list'
    if '\\begin{itemize}' in content[0]:
        type = 'list'
    if '\\item' in content[0]:
        type = 'list_item'
    # Create entry based on detected type
    entry_list = []
    if type == 'equation':
        entry_list.append(datastore.Entry(root_key + ' eq' + str(child_index), root_key, '\n'.join(content), 'equation', child_index))
    elif type == 'paragraph':
        entry_list.append(datastore.Entry(root_key + ' p' + str(child_index), root_key, '\n'.join(content), 'paragraph', child_index))
    elif type == 'ordered_list':
        entry_list.append(datastore.Entry(root_key + ' ol' + str(child_index), root_key, '', 'ordered_list', child_index))
    elif type == 'list':
        entry_list.append(datastore.Entry(root_key + ' ul' + str(child_index), root_key, '', 'list', child_index))
    elif type == 'list_item':
        entry_list.append(datastore.Entry(root_key + ' li' + str(child_index), root_key, '', 'list_item', child_index))
    if type == 'ordered_list' or type == 'list':
        item_pos = []
        for i in range(0, len(content)):
            if (content[i] == '\\item'):
                item_pos.append(i)
        # The end of list content is len(content) - 1 since last line is \end{...}
        item_pos.append(len(content) - 1)
        for i in range(0, len(item_pos) - 1):
            entry_list += create_latex_node(content[item_pos[i]:item_pos[i + 1]], entry_list[0].key, i + 1)
    elif type == 'list_item':
        entry_list += parse_latex_content(content[1:], entry_list[0].key)
    return entry_list

def parse_latex_content(content, root_key):
    if len(content) == 0:
        return []
    # If there are section partition points, parse the contents based on them
    prefix_list = ['\\section{', '\\subsection{', '\\subsubsection{', 
                   '\\paragraph{', '\\subparagraph{']
    for prefix in prefix_list:
        sec_list = get_parse_point(content, prefix)
        if len(sec_list) > 0:        
            # In order to extract the last partition
            sec_list.append(len(content))
            # Parse all partitions
            entry_list = []
            entry_list += parse_latex_content(content[0:sec_list[0]], root_key)
            for i in range(0, len(sec_list) - 1):
                sec_entry = datastore.Entry(root_key + '.' + str(i + 1), root_key, 
                                            str_strip(content[sec_list[i]], prefix, '}'),
                                            'title', i + 1)
                entry_list.append(sec_entry)
                content_sublist = content[sec_list[i] + 1:sec_list[i + 1]]
                entry_list += parse_latex_content(content_sublist, sec_entry.key)
            return entry_list
            
    # Otherwise, parse the contents based on empty lines
    sec_list = [-1]
    counter = 0
    for i in range(0, len(content)):
        if '\\begin{' in content[i]:
            counter += 1
        elif '\\end{' in content[i]:
            counter -= 1
        elif content[i] == '' and counter == 0:
            sec_list.append(i)
    sec_list.append(len(content))
    # Parse all partitions
    entry_list = []
    child_index = 1
    for i in range(0, len(sec_list) - 1):
        if sec_list[i] + 1 != sec_list[i + 1]:
            new_node_list = create_latex_node(content[sec_list[i] + 1:sec_list[i + 1]], root_key, child_index)
            child_index += 1
            entry_list += new_node_list
    return entry_list

