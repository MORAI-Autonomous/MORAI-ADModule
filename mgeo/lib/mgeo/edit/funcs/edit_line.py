def delete_line(line_set, line):
        """선택한 라인을 삭제한다"""
        if line_set is None:
            raise BaseException('None is passed for an argument line_set')

        if line is None:
            raise BaseException('None is passed for an argument line')
            return

        if line.included_plane:
            raise BaseException('This line has a plane associated to it\
                please delete the plane first')
            return

        # 연결된 노드에서 line에 대한 reference를 제거한다
        to_node = line.get_to_node()
        from_node = line.get_from_node()

        to_node.remove_from_links(line)
        from_node.remove_to_links(line)

        # Line Set에서 line에 대한 reference를 제거한다
        line_set.remove_line(line)