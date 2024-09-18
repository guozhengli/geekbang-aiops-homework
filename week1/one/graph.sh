#!/bin/bash

# 生成未处理的 DOT 文件
terraform graph > temp_graph.dot

# 创建一个新的 DOT 文件，添加颜色和样式
cat <<EOF > graph.dot
digraph G {
    compound = "true"
    newrank = "true"
    nodesep = "0.40"
    ranksep = "0.50"
    node [style="filled", fillcolor="lightblue", shape="box", color="black"]
    edge [color="gray"]
EOF

# Append the original DOT content to the new DOT file
tail -n +2 temp_graph.dot >> graph.dot

# Close the graph definition in the new DOT file
echo "}" >> graph.dot

# 删除临时文件
rm temp_graph.dot

# 生成带颜色的 PNG 图像
dot -Tpng graph.dot -o graph.png
