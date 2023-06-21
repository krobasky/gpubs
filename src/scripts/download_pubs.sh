#!/bin/bash

# Usage function
usage() {
  echo "Usage: $0 -n <number_of_files> [-v]"
  echo "Options:"
  echo "  -n <number_of_files>: Number of files to download (use -1 for all files)"
  echo "  -d <download_dir>: Set the directory to download the files to"
  echo "  -v <mode>: Verbose level, 0= no output. 1=warnings/errors. 2=info; default=0"
  echo "  -r: Refresh files (don't skip any that exist)."
  echo "  -h: Display this help message"
  echo ""
  echo "Example:"
  echo "  $0  -n 4 -d v4/data/raw/pubs -v 2 2> download.err"
  exit 1
}

refresh="False"
verbose_mode=0

# Parse command line options
while getopts "n:d:v:rh" opt; do
  case $opt in
    n)
      num_files=$OPTARG
      ;;
    d)
      download_dir=$OPTARG
      ;;
    v)
      verbose_mode=$OPTARG
      ;;
    h)
      usage
      ;;
    r)
      refresh="True"
      ;;
    *)
      usage
      ;;
  esac
done

# Check if the number of files is provided
if [ -z "$num_files" ]; then
  echo "Error: Number of files not provided!"
  usage
fi

# Check if the download directory is provided
if [ -z "$download_dir" ]; then
  echo ""
  echo "Error: Download directory is not provided!"
  echo ""
  usage
fi

# check if download directory exists
if [ ! -d "$download_dir" ]; then
  echo ""
  echo "Error: $download_dir is not a directory!"
  echo ""
  usage
fi

if [ $verbose_mode -ge 2 ]; then
    echo "Download Directory: $download_dir"
    echo "Number of abstracts to ensure have been downloaded: $num_files"
    echo "Refresh: $refresh"
fi

# FTP settings
ftp_host="ftp.ncbi.nlm.nih.gov"
ftp_path="/pubmed/baseline/"

# Retrieve file names and find the largest number
file_list=$(curl -s ftp://${ftp_host}${ftp_path} | awk '{print $NF}' | grep -E "^pubmed23n[0-9]{4}.xml.gz$" | sort -r)
latest_files=($(echo "$file_list" | head -n "$num_files"))

# Check if enough files are available
if (( ${#latest_files[@]} == 0 )); then
  echo "Error: Insufficient number of files available!"
  exit 1
fi

# Calculate total predicted size
total_size=0
for file_name in "${latest_files[@]}"; do
  file_size=$(curl -sI ftp://${ftp_host}${ftp_path}${file_name} | awk '/Content-Length/ {print $2}' | tr -d '\r')
  total_size=$((total_size + file_size))
done

# Check disk space function
check_disk_space() {
  local predicted_size=$1
  local required_space=$(echo "$predicted_size")
  local available_space=$(df -PB1 "$download_dir" | awk 'NR==2{print $4}')
  local required_space_human=$(numfmt --to=iec-i --suffix=B $required_space)
  local available_space_human=$(numfmt --to=iec-i --suffix=B $available_space)
  
  if [ $verbose_mode -ge 1 ]; then
      echo "Predicted download size = $required_space_human, Available space = $available_space_human"
  fi
  
  if (( required_space > available_space )); then
    echo "Insufficient disk space! Required: ${required_space_human}, Available: ${available_space_human}"
    exit 1
  fi
}

# Check disk space before downloading
check_disk_space $total_size

# Download and check files
for file_name in "${latest_files[@]}"; do

  md5_file_name="${file_name}.md5"

  # Refresh files that were previously downloaded?
  if [ $refresh == "False" ]; then 
      # No, so skip downloading those again

      # If one file or the other is missing, you still have to do a download
      # Here, just provide information as to which files are present.
      if [ $verbose_mode -ge 1 ]; then
	  if [ -f "${download_dir}/${file_name}"] && [ ! -f "${download_dir}/${md5_file_name}"] ; then
	      echo "ERROR:  Missing - ${download_dir}/${md5_file_name}; re-downloading now"
	  fi
	  if [ ! -f "${download_dir}/${file_name}"] && [ -f "${download_dir}/${md5_file_name}"] ; then
	      echo "ERROR:  Missing - ${download_dir}/${file_name}; re-downloading now"
	  fi
      fi

      if [ -f "${download_dir}/${file_name}" ] && [ -f "${download_dir}/${md5_file_name}" ]; then
	  if [ $verbose_mode -ge 1 ]; then
	      echo "SKIP: ${download_dir}/${file_name} exists."
	  fi
	  continue
      fi
 fi

  # Check file size
  file_size=$(curl -sI ftp://${ftp_host}${ftp_path}${file_name} | awk '/Content-Length/ {print $2}' | tr -d '\r')


  if [ $verbose_mode -ge 2 ]; then
      echo "File: $file_name, Size: ${file_size} bytes"
  fi

  # Download file
  if [ $verbose_mode -ge 1 ]; then
    echo "WARNING: Downloading: $file_name to ${download_dir}"
  fi
  rm -f "${download_dir}/${file_name}"
  curl -o "${download_dir}/${file_name}"  ftp://${ftp_host}${ftp_path}${file_name}

  # Download MD5 file
  rm -f "${download_dir}/${md5_file_name}"
  curl -o "${download_dir}/${md5_file_name}"  ftp://${ftp_host}${ftp_path}${md5_file_name}

  # Check MD5
  pushd ${download_dir} > /dev/null
  md5sum -c "${md5_file_name}" >/dev/null 2>&1
  if [ $? -eq 0 ]; then
      if [ $verbose_mode -ge 2 ]; then
	  echo "${md5_file_name}: OK - MD5 checksum verification succeeded."
      fi
  else
      if [ $verbose_mode -ge 1 ]; then
	  echo "ERROR: ${md5_file_name}: FAILED - MD5 checksum verification failed."
      fi
  fi
  popd > /dev/null

done

if [ $verbose_mode -ge 2 ]; then
    total_size_human=$(numfmt --to=iec-i --suffix=B $total_size)
    echo "Total size of abstract files: ${total_size_human}"
fi
