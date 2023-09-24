import argparse
import wave
import time

def distort(value,amount): # expects a value between -1 and 1
	return value-(amount*((1/3)*(value**3)))

parser=argparse.ArgumentParser(description="Fattens a wave file")
parser.add_argument("input_file", type=argparse.FileType("r"),help="The name of the original file")
parser.add_argument("output_file", type=argparse.FileType("w"),help="The name of the fattened file")
parser.add_argument("-v", "--verbose", action="store_true", help="Shows additional information about the file as it's being fattened")
parser.add_argument("-p", "--passes", type=int, default=20, help="Amount of times to filter the file (default: 20)")
parser.add_argument("-l", "--lowpass", type=int, default=3, help="Fraction of passes for the lowpass filter (default: 3)")
parser.add_argument("-d", "--distort",  type=int, default=0, help="Apply soft clipping to the signal, with adjustable intensity")
parser.add_argument("-sb", "--sixteen_bit", action="store_true", help="If the input file is 8-bit, the resulting file will be 16-bit, without converting back")

args=parser.parse_args()
input_file=args.input_file.name
output_file=args.output_file.name
verbose=args.verbose
filter_passes=args.passes
filter_passes_fraction=args.lowpass
distortion=args.distort
sixteen_bit=args.sixteen_bit

print("16fatten v1.0.0")
print("by Presley Peters, 2023")
print()

success=True
try:
	wave_file=wave.open(input_file,"r")
	input_stereo=wave_file.getnchannels()==2
	input_bit_depth=wave_file.getsampwidth()
	input_sample_rate=wave_file.getframerate()
	file_orig=list(wave_file.readframes(wave_file.getnframes()))
	wave_file.close()

	position=0
	file_lowpass_halfway=[]
	file_length_adjusted=len(file_orig)
	if input_bit_depth==1:
		file_length_adjusted*=2
	file_highpass=[0]*file_length_adjusted
	loop_length=file_length_adjusted
	lowpass_passes=filter_passes//filter_passes_fraction

	loop_length-=2
	if input_stereo:
		loop_length-=4
	else:
		loop_length-=2
except:
	success=False
	print("Error opening input file!")

if success:
	if input_bit_depth>2:
		print("Error: Bit depth not supported!")
	elif input_file.split(".")[-1].lower()!="wav":
		print("Error: Input file isn't a wave file!")
	else:
		if filter_passes_fraction<1:
			print("Warning: Fraction can't be below 1! Using 1...")
			print()
		if filter_passes//filter_passes_fraction==0 and filter_passes!=1:
			filter_passes_fraction=1
			print("Warning: Fraction too high! Using 1...")
			print()
		if verbose:
			if input_bit_depth==1:
				print("Bit depth: 8 bit")
			elif input_bit_depth==2:
				print("Bit depth: 16 bit")
			print("Sample rate: " + str(input_sample_rate) + " Hz")
			print("Stereo: " + str(input_stereo))
			input_length_seconds=len(file_orig)/input_sample_rate
			if input_stereo:
				input_length_seconds/=2
			if input_bit_depth==2:
				input_length_seconds/=2
			print("Length: " + str(round(input_length_seconds,2)) + " seconds")
			print("File size: " + str(round(len(file_orig)/1000)) + " KB")
			print()
		else:
			print("Fattening...")
		print_delay=80000

		start_time=time.perf_counter()

		if input_bit_depth==1:
			multiplier=65535/255
			counter=0
			file_sixteen=[]
			while len(file_orig)>0:
				if counter%200==0 and verbose:
					percent=round(((counter*2)/file_length_adjusted)*100,2)
					print("Converting to 16 bit... " + str(percent) + "%   ",end="\r")
				byte=int((file_orig.pop(0)*multiplier)+32768) & 65535
				file_sixteen.append(byte & 255)
				file_sixteen.append(byte>>8)
				counter+=1
			file_orig=file_sixteen.copy()
			file_sixteen.clear()
			if verbose:
				print("Converting to 16 bit... 100.0%   ")

		position=0
		while position<loop_length:
			if position%print_delay==0 and verbose:
				percent=round((position/len(file_orig))*100,2)
				print("Scaling... " + str(percent) + "%   ",end="\r")

			byte=((file_orig[position] | (file_orig[position+1]<<8))+32768) & 65535
			byte-=32768
			byte=int(byte*0.5)
			byte=byte & 65535
			file_orig[position]=byte & 255
			file_orig[position+1]=byte>>8
			position+=2
		file_lowpass=file_orig.copy()
		if verbose:
			print("Scaling... 100.0%   ")

		for a in range(0,filter_passes):
			position=0
			while position<loop_length:
				if position%print_delay==0 and verbose:
					percent=round((position/len(file_orig))*100,2)
					print("Filtering (" + str(a+1) + "/" + str(filter_passes) + ")... " + str(percent) + "%   ",end="\r")
				if input_stereo:
					byte_1=((file_lowpass[position] | (file_lowpass[position+1]<<8))+32768) & 65535
					byte_2=((file_lowpass[position+4] | (file_lowpass[position+5]<<8))+32768) & 65535

					byte=(((byte_1+byte_2)//2)+32768) & 65535
					file_lowpass[position]=byte & 255
					file_lowpass[position+1]=byte>>8

					byte_orig=(file_orig[position] | (file_orig[position+1]<<8)+32768) & 65535
					byte_high=(byte_orig-abs(0-byte))
					byte_high=(byte_high+32768) & 65535
					file_highpass[position]=byte_high & 255
					file_highpass[position+1]=byte_high>>8

					byte_1=((file_lowpass[position+2] | (file_lowpass[position+3]<<8))+32768) & 65535
					byte_2=((file_lowpass[position+6] | (file_lowpass[position+7]<<8))+32768) & 65535
					byte=(((byte_1+byte_2)//2)+32768) & 65535
					file_lowpass[position+2]=byte & 255
					file_lowpass[position+3]=byte>>8

					byte_orig=((file_orig[position+2] | (file_orig[position+3]<<8))+32768) & 65535
					byte_high=(byte_orig-abs(0-byte))+32768
					byte_high=byte_high & 65535
					file_highpass[position+2]=byte_high & 255
					file_highpass[position+3]=byte_high>>8

					position+=4
				else:
					byte_orig=file_lowpass[position] | (file_lowpass[position+1]<<8)
					byte_1=((file_lowpass[position] | (file_lowpass[position+1]<<8))+32768) & 65535
					byte_2=((file_lowpass[position+2] | (file_lowpass[position+3]<<8))+32768) & 65535
					byte=(((byte_1+byte_2)//2)+32768) & 65535
					file_lowpass[position]=byte & 255
					file_lowpass[position+1]=byte>>8

					byte_orig=((file_orig[position] | (file_orig[position+1]<<8))+32768) & 65535
					byte_high=((byte_orig-abs(0-byte))+32768) & 65535
					file_highpass[position]=byte_high & 255
					file_highpass[position+1]=byte_high>>8

					position+=2
			if a==lowpass_passes:
				file_lowpass_halfway=file_lowpass.copy()

		file_lowpass.clear()
		if verbose:
			print("Filtering (" + str(filter_passes) + "/" + str(filter_passes) + ")... 100.0%   ")
		position=0

		while position<loop_length:
			if position%print_delay==0 and verbose:
				percent=round((position/len(file_orig))*100,2)
				print("Mixing... " + str(percent) + "%   ",end="\r")
			byte_low=((file_lowpass_halfway[position] | (file_lowpass_halfway[position+1]<<8))+32768) & 65535
			byte_high=((file_highpass[position] | (file_highpass[position+1]<<8))+32768) & 65535
			byte=(byte_low+byte_high)//2
			byte=(byte+32768) & 65535
			file_orig[position]=byte & 255
			file_orig[position+1]=byte>>8
			position+=2
		file_lowpass_halfway.clear()
		file_highpass.clear()

		if verbose:
			print("Mixing... 100.0%   ")

		position=0

		loop_length=len(file_orig)
		if input_bit_depth==1:
			loop_length-=1
		elif input_bit_depth==2:
			loop_length-=2

		loudest=0
		if distortion>0:
			while position<loop_length:
				if position%print_delay==0 and verbose:
					percent=round((position/len(file_orig))*100,2)
					print("Distorting... " + str(percent) + "%   ",end="\r")
				byte=((file_orig[position] | (file_orig[position+1]<<8))+32768) & 65535
				byte-=32768
				byte_sign=byte/32768
				byte=int(distort(byte_sign,distortion)*32768)
				if abs(byte)>loudest:
					loudest=abs(byte)
				byte+=32768
				byte=(byte+32768) & 65535
				file_orig[position]=byte & 255
				file_orig[position+1]=byte>>8
				position+=2

			if verbose:
				print("Distorting... 100.0%   ")
		else:
			while position<loop_length:
				byte=((file_orig[position] | (file_orig[position+1]<<8))+32768) & 65535
				byte-=32768
				if abs(byte)>loudest:
					loudest=abs(byte)
				position+=2

		loudest*=2
		scale_amount=65535/loudest

		position=0
		while position<loop_length:
			if position%print_delay==0 and verbose:
				percent=round((position/len(file_orig))*100,2)
				print("Normalizing... " + str(percent) + "%   ",end="\r")
			byte=((file_orig[position] | (file_orig[position+1]<<8))+32768) & 65535
			byte-=32768
			byte=int(byte*scale_amount)
			byte+=32768
			byte=(byte+32768) & 65535
			file_orig[position]=byte & 255
			file_orig[position+1]=byte>>8
			position+=2
		if verbose:
			print("Normalizing... 100.0%   ")

		if input_bit_depth==1 and not sixteen_bit:
			for a in range(0,len(file_orig)//2):
				if a%200==0 and verbose:
					percent=round(((a*2)/file_length_adjusted)*100,2)
					print("Converting back to 8 bit... " + str(percent) + "%   ",end="\r")
				file_orig.pop(a)
				file_orig[a]=(file_orig[a]+128) & 255
			if verbose:
				print("Converting back to 8 bit... 100.0%   ")

		if sixteen_bit:
			input_bit_depth=2

		end_time=time.perf_counter()

		wave_file=wave.open(output_file,"w")
		if input_stereo:
			wave_file.setnchannels(2)
		else:
			wave_file.setnchannels(1)
		wave_file.setsampwidth(input_bit_depth)
		wave_file.setframerate(input_sample_rate)
		wave_file.writeframesraw(bytearray(file_orig))
		wave_file.close()

		print("Fattened in " + str(round(end_time-start_time,2)) + " seconds!")